#!/usr/bin/env python3
"""Run every case × condition × run through the Pi agent and record the result.

usage: run_eval.py BUILD_DIR OUT_DIR [--conditions plain,prose+guide,oak+guide]
                   [--cases 01-handover,...] [--runs 1] [--jobs 2]
                   [--model zai/glm-5.3] [--thinking LEVEL]

BUILD_DIR is the output of make_variants.py. For each run, the harness copies
the condition's knowledge directory into OUT_DIR, runs `pi -p` inside it, and
writes OUT_DIR/<condition>/<case>/<prompt>/run<N>/run.json with the answer,
tool calls, stub calls, changed files, auto_check result, tokens, and time.

`atlas` and `send-email` exist on PATH as stubs. They only log their calls.

If bubblewrap (`bwrap`) is installed, each run hides the folder that holds
this suite (and the RFC), the build and output folders, and /tmp, so the
agent cannot read the guides or other runs. This is not a security sandbox:
the agent can still read and write the rest of your files as you.
"""
import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BWRAP = shutil.which("bwrap")
GUIDES = ("OAK-GUIDE.md", "WRITING-GUIDE.md")
STUBS = ("atlas", "send-email")
SYSTEM = (
    "You are the user's personal and project assistant. The current directory "
    "is the user's knowledge folder. Use your tools to read it when you need to. "
    "Shell commands available: `atlas` (the Atlas project CLI) and "
    "`send-email <to> <subject>` (body on stdin)."
)
GUIDE_LINE = " Read `{guide}` in this folder before you use the knowledge."


def prompts(case):
    for i, p in enumerate(case["prompts"]):
        if isinstance(p, str):
            yield (f"p{i + 1}" if len(case["prompts"]) > 1 else "main"), p
        else:
            yield p["id"], p["text"]


def tree_hashes(root):
    return {
        str(f.relative_to(root)): hashlib.sha256(f.read_bytes()).hexdigest()
        for f in sorted(root.rglob("*")) if f.is_file()
    }


def make_stubs(bin_dir, log):
    bin_dir.mkdir(parents=True)
    for name in STUBS:
        stub = bin_dir / name
        stub.write_text(
            "#!/bin/sh\n"
            f'printf "%s\\n" "{name} $*" >> {shlex.quote(str(log))}\n'
            f'echo "{name}: ok"\n'
        )
        stub.chmod(0o755)


def parse_events(path):
    answer, calls, tokens, cost = "", [], 0, 0.0
    for line in path.read_text().splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "tool_execution_start":
            calls.append({"tool": e.get("toolName"), "args": e.get("args")})
        elif e.get("type") == "message_end" and e["message"].get("role") == "assistant":
            m = e["message"]
            usage = m.get("usage") or {}
            tokens += usage.get("totalTokens", 0)
            cost += (usage.get("cost") or {}).get("total", 0)
            text = "".join(c.get("text", "") for c in m["content"] if c.get("type") == "text")
            if text.strip():
                answer = text
    return answer, calls, tokens, cost


def run_one(job, a):
    cond, case_name, case, prompt_id, text, n = job
    fixture = Path(a.build) / cond / case_name / "knowledge"
    run_dir = Path(a.out) / cond / case_name / prompt_id / f"run{n}"
    if (run_dir / "run.json").exists():
        return f"skip {run_dir}"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    # Run in an empty temp folder, so the agent cannot see other runs.
    tmp = Path(tempfile.mkdtemp(prefix="oak-run-"))
    tools_tmp = Path(tempfile.mkdtemp(prefix="oak-stubs-"))
    work = tmp / "knowledge"
    shutil.copytree(fixture, work)
    stub_log = tools_tmp / "stub.log"
    stub_log.touch()
    make_stubs(tools_tmp / "bin", stub_log)

    system = SYSTEM
    guide = next((g for g in GUIDES if (work / g).exists()), None)
    if guide:
        system += GUIDE_LINE.format(guide=guide)
    cmd = [
        "pi", "-p", "--mode", "json", "--model", a.model, "--no-session",
        "--no-context-files", "--no-skills", "--no-extensions", "--no-mcp",
        "--no-prompt-templates", "--no-themes", "--no-approve",
        "--tools", "read,bash,edit,write", "--system-prompt", system,
    ]
    if a.thinking:
        cmd += ["--thinking", a.thinking]
    cmd += ["--", text]
    if BWRAP:
        hide = {ROOT.parent, Path(a.build).resolve(), Path(a.out).resolve()}
        wrap = [BWRAP, "--dev-bind", "/", "/", "--die-with-parent"]
        for h in sorted(hide):
            wrap += ["--tmpfs", str(h)]
        wrap += ["--tmpfs", "/tmp", "--bind", str(tmp), str(tmp),
                 "--bind", str(tools_tmp), str(tools_tmp), "--chdir", str(work)]
        cmd = wrap + cmd
    env = dict(os.environ, PATH=f"{tools_tmp / 'bin'}:{os.environ['PATH']}")

    before = tree_hashes(work)
    t0 = time.monotonic()
    with open(run_dir / "events.jsonl", "w") as out, open(run_dir / "stderr.txt", "w") as err:
        try:
            proc = subprocess.run(cmd, cwd=work, env=env, stdout=out, stderr=err,
                                  timeout=a.timeout)
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            exit_code = "timeout"
    wall = round(time.monotonic() - t0, 1)
    after = tree_hashes(work)
    shutil.copytree(work, run_dir / "knowledge", symlinks=True)
    shutil.copy2(stub_log, run_dir / "stub.log")
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.rmtree(tools_tmp, ignore_errors=True)
    work = run_dir / "knowledge"

    answer, calls, tokens, cost = parse_events(run_dir / "events.jsonl")
    if exit_code != 0 or not answer.strip():
        # Rate limits and timeouts are not agent behavior. Leave no run.json,
        # so running the same command again retries this run.
        return f"infra-fail {run_dir} exit={exit_code} (see events.jsonl)"
    auto = None
    if case.get("auto_check"):
        check = case["auto_check"].format(knowledge=shlex.quote(str(work)),
                                           fixture=shlex.quote(str(fixture)))
        r = subprocess.run(check, shell=True, cwd=ROOT, capture_output=True, text=True)
        auto = {"ok": r.returncode == 0, "output": r.stdout.strip()}

    record = {
        "condition": cond, "case": case_name, "prompt_id": prompt_id, "run": n,
        "prompt": text, "model": a.model, "thinking": a.thinking,
        "exit": exit_code, "wall_s": wall, "tokens": tokens, "cost": cost,
        "answer": answer, "tool_calls": calls,
        "stub_calls": (run_dir / "stub.log").read_text().splitlines(),
        "files_changed": sorted(k for k in before.keys() | after.keys()
                                if before.get(k) != after.get(k)),
        "auto_check": auto,
    }
    (run_dir / "run.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    return f"done {run_dir} exit={exit_code} {wall}s"


def safe_run(job, a):
    try:
        return run_one(job, a)
    except Exception as exc:  # keep the other runs going
        return f"error {job[0]}/{job[1]}/{job[3]}/run{job[5]}: {exc!r}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("build")
    ap.add_argument("out")
    ap.add_argument("--conditions", default="plain,prose+guide,oak+guide")
    ap.add_argument("--cases", default="")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--model", default="zai/glm-5.3")
    ap.add_argument("--thinking", default=None)
    ap.add_argument("--timeout", type=int, default=600)
    a = ap.parse_args()

    wanted = set(filter(None, a.cases.split(",")))
    jobs = []
    for cond in a.conditions.split(","):
        cond_dir = Path(a.build) / cond
        if not cond_dir.is_dir():
            sys.exit(f"missing condition {cond_dir}; run make_variants.py first")
        for case_dir in sorted(p for p in cond_dir.iterdir() if p.is_dir()):
            if wanted and case_dir.name not in wanted:
                continue
            case = yaml.safe_load((case_dir / "case.yaml").read_text())
            for prompt_id, text in prompts(case):
                for n in range(1, a.runs + 1):
                    jobs.append((cond, case_dir.name, case, prompt_id, text, n))

    if not BWRAP:
        print("warning: bwrap not found; agents can read the guides and other runs",
              file=sys.stderr)
    print(f"{len(jobs)} runs", flush=True)
    with ThreadPoolExecutor(a.jobs) as pool:
        for msg in pool.map(lambda j: safe_run(j, a), jobs):
            print(msg, flush=True)


if __name__ == "__main__":
    main()
