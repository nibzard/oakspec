#!/usr/bin/env python3
"""Unified CLI for the OAK Gym (`code`, `prose`, `check`, and `list`).

Examples:
  python3 gym/harness/run.py list
  python3 gym/harness/run.py check path/to/knowledge
  python3 gym/harness/run.py code --mode single --agents claude_opus_5_5 --output runs/code-check
  python3 gym/harness/run.py prose --mode all --agents claude_opus_5_5,codex_gpt_6_2_sol,pi_glm_5_4,agy_gemini_4_neon --output runs/prose-check
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from gym.harness.check_oak import check_knowledge_dir
from gym.harness.sandboxes import SUPPORTED_AGENTS
from gym.suites.code.suite import run_code_suite
from gym.suites.prose.suite import run_prose_suite


def default_out(suite_name: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return REPO_ROOT / "runs" / f"{suite_name}-{stamp}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List standardized OAK Gym suites, substrates, and agents")

    p_chk = sub.add_parser("check", help="Run deterministic OAK-0001 v0.5 linter on a knowledge folder")
    p_chk.add_argument("knowledge_dir", type=Path)
    p_chk.add_argument("--project-root", type=Path, default=None)

    for sname in ("code", "prose"):
        p = sub.add_parser(sname, help=f"Run the standardized {sname} gym suite")
        p.add_argument("--mode", choices=("single", "relay", "all"), default="single")
        p.add_argument("--agents", default="claude_opus_5_5", help="Comma-separated agent IDs")
        p.add_argument("--output", type=Path, default=None)

    args = ap.parse_args()
    if args.cmd == "list":
        info = {
            "suites": {
                "code": "pallets/itsdangerous (BSD-3-Clause, 297 pytest tests) — real Python coding + OAK policy/scope/merge",
                "prose": "SCP Antimemetics Division Hub (CC BY-SA 3.0, qntm) — book authoring, revoked reveals, canon vs brainstorm, editorial relay",
                "micro": "gym/suites/micro/ — fast Gondolin VM ablations (bootstrap, R1/R4/R5 probes, W9 digests)",
            },
            "supported_agents": list(SUPPORTED_AGENTS),
        }
        print(json.dumps(info, indent=2))
        return 0

    if args.cmd == "check":
        res = check_knowledge_dir(args.knowledge_dir, args.project_root)
        print(json.dumps(res, indent=2))
        return 0 if res["valid"] else 1

    agents = [a.strip() for a in args.agents.split(",") if a.strip()]
    for a in agents:
        if a not in SUPPORTED_AGENTS:
            sys.exit(f"Unsupported agent {a!r}; choose from {SUPPORTED_AGENTS}")
    out_dir = args.output or default_out(args.cmd)
    res = run_code_suite(out_dir, args.mode, agents) if args.cmd == "code" else run_prose_suite(out_dir, args.mode, agents)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
