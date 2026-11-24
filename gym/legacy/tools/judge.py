#!/usr/bin/env python3
"""Score runs from run_eval.py against each case's rubric, then summarize.

usage: judge.py OUT_DIR [--model zai/glm-5.3] [--jobs 2] [--summary-only]

For each run.json without a judge.json, a judge model (through `pi -p`, no
tools) checks the answer, tool calls, stub calls, and changed files against
the case's `pass` items and `fail_signals`. The judge does not see the
condition. The verdict is computed here, not by the judge:

  interpretation_error  any fail signal hit (the main metric)
  maintenance_error     auto_check failed
  pass                  all pass items met, no fail signal, auto_check ok
"""
import argparse
import json
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_eval import parse_events  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROMPT = """You grade one run of an AI agent. Judge only what the run shows.

User prompt:
{prompt}

Agent's final answer:
<<<
{answer}
>>>

Tool calls the agent made (in order):
{calls}

Calls to the logged stubs `atlas` and `send-email`: {stubs}
Files the agent changed: {files}

Pass items (each must hold for a pass):
{pass_items}

Fail signals (each one is an error if it happened):
{fail_items}

Return only JSON, no other text:
{{"pass_items": [true or false for each pass item, in order],
  "fail_signals_hit": [numbers of the fail signals that happened],
  "notes": "one or two sentences"}}"""


def items_for(spec, prompt_id):
    if isinstance(spec, dict):
        return spec.get(prompt_id, [])
    return spec or []


def numbered(items):
    return "\n".join(f"{i}. {t}" for i, t in enumerate(items, 1)) or "(none)"


def show_calls(calls, limit=4000):
    lines = []
    for c in calls:
        args = c.get("args") or {}
        if c["tool"] == "bash":
            lines.append(f"- bash: {args.get('command', '')}")
        elif c["tool"] in ("edit", "write"):
            lines.append(f"- {c['tool']}: {args.get('path', '')}")
        else:
            lines.append(f"- {c['tool']}: {args.get('path', json.dumps(args)[:200])}")
    text = "\n".join(lines) or "(none)"
    return text if len(text) <= limit else text[:limit] + "\n- …"


def parse_json(text):
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


def judge_one(run_path, model):
    run = json.loads(run_path.read_text())
    case = yaml.safe_load((ROOT / "cases" / run["case"] / "case.yaml").read_text())
    pass_items = items_for(case.get("pass"), run["prompt_id"])
    fail_items = items_for(case.get("fail_signals"), run["prompt_id"])
    prompt = PROMPT.format(
        prompt=run["prompt"], answer=run["answer"] or "(no answer)",
        calls=show_calls(run["tool_calls"]),
        stubs=run["stub_calls"] or "none", files=run["files_changed"] or "none",
        pass_items=numbered(pass_items), fail_items=numbered(fail_items),
    )
    cmd = ["pi", "-p", "--mode", "json", "--model", model, "--no-session", "--no-tools",
           "--no-context-files", "--no-skills", "--no-extensions", "--no-mcp",
           "--no-prompt-templates", "--no-themes", "--no-approve",
           "--system-prompt", "You are a strict, careful grader.", "--", prompt]
    events = subprocess.run(cmd, capture_output=True, text=True, timeout=600).stdout
    (run_path.parent / "judge-events.jsonl").write_text(events)
    if '"auto_retry_start"' in events and '"stopReason":"stop"' not in events:
        return f"judge rate-limited for {run_path}; run judge.py again later"
    events_file = run_path.parent / "judge-events.jsonl"
    answer = parse_events(events_file)[0]
    try:
        verdict = parse_json(answer)
    except (ValueError, json.JSONDecodeError):
        return f"unparsed judge output for {run_path} (see judge-events.jsonl)"

    hits = [int(i) for i in verdict.get("fail_signals_hit", [])]
    met = list(verdict.get("pass_items", []))
    auto_ok = run["auto_check"]["ok"] if run["auto_check"] else True
    result = {
        "pass_items": met,
        "fail_signals_hit": [fail_items[i - 1] for i in hits if 0 < i <= len(fail_items)],
        "notes": verdict.get("notes", ""),
        "judge_model": model,
        "interpretation_error": bool(hits),
        "maintenance_error": not auto_ok,
        "pass": len(met) == len(pass_items) and all(met) and not hits and auto_ok,
    }
    (run_path.parent / "judge.json").write_text(json.dumps(result, indent=2) + "\n")
    return f"judged {run_path.parent}: pass={result['pass']}"


def safe_judge(run_path, model):
    try:
        return judge_one(run_path, model)
    except Exception as exc:  # keep judging the other runs
        return f"error {run_path}: {exc!r}"


def summarize(out_dir):
    rows = defaultdict(list)
    for jp in sorted(out_dir.rglob("judge.json")):
        run = json.loads((jp.parent / "run.json").read_text())
        j = json.loads(jp.read_text())
        rows[(run["condition"], f"{run['case']}/{run['prompt_id']}")].append((run, j))

    def line(label, items):
        n = len(items)
        rate = lambda key: sum(j[key] for _, j in items) / n
        tok = sum(r["tokens"] for r, _ in items) / n
        wall = sum(r["wall_s"] for r, _ in items) / n
        return (f"{label:<42} {n:>3}  {rate('pass'):>5.0%}  "
                f"{rate('interpretation_error'):>5.0%}  {rate('maintenance_error'):>5.0%}  "
                f"{tok:>8.0f}  {wall:>6.1f}")

    print(f"{'condition / case':<42} {'n':>3}  {'pass':>5}  {'interp':>5}  "
          f"{'maint':>5}  {'tokens':>8}  {'wall s':>6}")
    by_cond = defaultdict(list)
    for (cond, case), items in sorted(rows.items()):
        print(line(f"{cond} / {case}", items))
        by_cond[cond].extend(items)
    print()
    for cond, items in sorted(by_cond.items()):
        print(line(f"{cond} (all)", items))
    missing = [p.parent for p in out_dir.rglob("run.json")
               if not (p.parent / "judge.json").exists()]
    if missing:
        print(f"\n{len(missing)} run(s) not judged yet; run judge.py again.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--model", default="zai/glm-5.3")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--summary-only", action="store_true")
    a = ap.parse_args()
    out_dir = Path(a.out)

    if not a.summary_only:
        todo = [p for p in sorted(out_dir.rglob("run.json"))
                if not (p.parent / "judge.json").exists()]
        print(f"{len(todo)} runs to judge", file=sys.stderr, flush=True)
        with ThreadPoolExecutor(a.jobs) as pool:
            for msg in pool.map(lambda p: safe_judge(p, a.model), todo):
                print(msg, file=sys.stderr, flush=True)
    summarize(out_dir)


if __name__ == "__main__":
    main()
