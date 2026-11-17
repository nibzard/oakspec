#!/usr/bin/env python3
"""Measure knowledge drift in the ohya repository, from its real history.

usage: ohya_drift.py [REPO] [LOOPER_STATE_DB]

Rules (each needs a different explicit field):

  R1 stale doc line   A Markdown line calls a task open, pending, next, or
                      blocked after the task finished.   (status + link)
  R2 stuck block      A task stays blocked after all its depends_on tasks
                      finished.                          (status + depends_on)
  R3 old "verified"   A NOTES.md bullet says "verified <date>" and names a
                      file that changed after that date. (as_of + sources)

R1 and R2 are replayed over history: task finish times come from Looper's
events, and Markdown content comes from git. R3 checks the current files.
Looper's own LLM review findings about drift are counted for comparison.
"""
import json
import re
import sqlite3
import statistics
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/agent/ohya")
STATE = Path(sys.argv[2] if len(sys.argv) > 2 else
             "/home/agent/.looper/ohya-3d80aa08/runtime/state.db")
GRACE = timedelta(hours=1)  # time allowed to update docs after a task ends
TASK_RE = re.compile(r"\bT(\d{3})\b")
OPEN_RE = re.compile(r"\b(stays? open|remains? open|still open|open item|open question|"
                     r"pending|todo|not yet|unvalidated|unresolved|outstanding|"
                     r"still blocked|is blocked|blocked on|blocked backlog|next step|"
                     r"comes next|deferred to|waits? for|waiting on|until|"
                     r"unblock condition|tracked (?:as|in|by)|follow-?up)\b", re.I)
DRIFT_FINDING_RE = re.compile(r"already exists|already met|already satisfied|"
                              r"stale|still blocked|no longer|out of date|outdated", re.I)


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")[:26] + "+00:00"
                                  if "." in s else s.replace("Z", "+00:00"))


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True,
                          text=True, check=True).stdout


def looper_events():
    db = sqlite3.connect(f"file:{STATE}?mode=ro", uri=True)
    return db.execute("select time, kind, message from events order by id").fetchall()


def finish_times(events):
    """First time each task finished (done or cancelled)."""
    out = {}
    for t, kind, msg in events:
        m = re.match(r"(T\d+)\s+done\b", msg) if kind == "result" else \
            re.match(r"Cancelled (T\d+)\.", msg) if kind == "cancel" else None
        if m and m.group(1) not in out:
            out[m.group(1)] = ts(t)
    return out


def r1_stale_doc_lines(finished):
    """Replay every commit that touched Markdown; track stale lines' lifetimes."""
    log = git("log", "--reverse", "--format=@@%H %cI", "--name-only", "--", "*.md")
    commits, cur = [], None
    for line in log.splitlines():
        if line.startswith("@@"):
            sha, when = line[2:].split(" ", 1)
            cur = (sha, datetime.fromisoformat(when), [])
            commits.append(cur)
        elif line.strip() and cur:
            cur[2].append(line.strip())
    content, open_flags, closed = {}, {}, []
    for sha, when, files in commits:
        for f in files:
            try:
                content[f] = git("show", f"{sha}:{f}").splitlines()
            except subprocess.CalledProcessError:
                content.pop(f, None)  # deleted at this commit
        seen = set()
        for f, lines in content.items():
            for text in lines:
                if not OPEN_RE.search(text):
                    continue
                for num in TASK_RE.findall(text):
                    task = f"T{num}"
                    done = finished.get(task)
                    if done and when > done + GRACE:
                        key = (f, task, text.strip())
                        seen.add(key)
                        open_flags.setdefault(key, (when, sha, done))
        for key in list(open_flags):
            if key not in seen:
                first, sha0, done = open_flags.pop(key)
                closed.append((key, first, when, done))
    return closed, open_flags


def r2_stuck_blocks(events, finished):
    tasks = {t["id"]: t for t in json.loads((REPO / "to-do.json").read_text())["tasks"]}
    blocked_at, started_at = {}, {}
    for t, kind, msg in events:
        m = re.match(r"(T\d+)\s+(\w+)", msg)
        if not m:
            continue
        if kind == "result" and m.group(2) == "blocked":
            blocked_at.setdefault(m.group(1), ts(t))
        if kind == "start":
            started_at.setdefault(m.group(1), []).append(ts(t))
    out = []
    for tid, b in blocked_at.items():
        deps = tasks.get(tid, {}).get("depends_on") or []
        if not deps or not all(d in finished for d in deps):
            continue
        ready = max([b] + [finished[d] for d in deps])
        later = [s for s in started_at.get(tid, []) if s > ready]
        end = later[0] if later else finished.get(tid)
        reason = (tasks[tid].get("block_reason") or {}).get("class", "?")
        out.append((tid, ready, end, reason))
    return out


def r3_old_verified():
    out = []
    for line in (REPO / "NOTES.md").read_text().splitlines():
        m = re.search(r"verified (?:\w+ )?(\d{4}-\d{2}-\d{2})", line)
        if not m:
            continue
        paths = {p for p in re.findall(r"`([\w./-]+\.\w+)`", line) if (REPO / p).exists()}
        changed = []
        for p in sorted(paths):
            last = git("log", "-1", "--format=%cI", "--", p).strip()
            if last and last[:10] > m.group(1):
                changed.append(f"{p} ({last[:10]})")
        if changed:
            out.append((m.group(1), changed, line.strip()[:140]))
    return out


def hours(d):
    return round(d.total_seconds() / 3600, 1)


def main():
    events = looper_events()
    finished = finish_times(events)
    print(f"tasks with a finish time from Looper: {len(finished)}\n")

    closed, still = r1_stale_doc_lines(finished)
    print(f"R1 stale doc lines: {len(closed)} fixed later, {len(still)} still present")
    if closed:
        life = [hours(end - first) for _, first, end, _ in closed]
        lag = [hours(first - done) for _, first, _, done in closed]
        print(f"   lifetime of fixed ones (h): median {statistics.median(life)}, max {max(life)}")
        print(f"   first seen after task end (h): median {statistics.median(lag)}")
    for (f, task, text), (first, sha, done) in sorted(still.items())[:25]:
        print(f"   OPEN {f}: {task} done {done:%m-%d %H:%M} | {text[:110]}")
    for (f, task, text), first, end, done in closed[:15]:
        print(f"   FIXED {f}: {task} stale {hours(end - first)}h | {text[:100]}")

    print()
    stuck = r2_stuck_blocks(events, finished)
    print(f"R2 stuck blocks (deps finished, task still blocked): {len(stuck)}")
    for tid, ready, end, reason in sorted(stuck, key=lambda x: x[1]):
        dur = f"{hours(end - ready)}h" if end else "still blocked"
        print(f"   {tid} ({reason}) ready {ready:%m-%d %H:%M} -> {dur}")

    print()
    old = r3_old_verified()
    print(f"R3 NOTES.md 'verified' claims whose named files changed later: {len(old)}")
    for date, changed, text in old[:12]:
        print(f"   verified {date}; changed: {', '.join(changed)[:90]}\n      {text}")

    print()
    findings = [(t, m) for t, k, m in events if k == "finding" and DRIFT_FINDING_RE.search(m)]
    print(f"Looper LLM review findings about drift: {len(findings)} "
          f"of {sum(1 for _, k, _ in events if k == 'finding')} findings")
    for t, m in findings[:10]:
        print(f"   {t[:16]} {m[:150].replace(chr(10), ' ')}")


if __name__ == "__main__":
    main()
