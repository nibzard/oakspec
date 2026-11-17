#!/usr/bin/env python3
"""Setup test: can an agent set up OAK memory from the RFC text alone?

usage: run_setup.py OUT_DIR [--agents pi,claude,codex] [--fixtures empty,messy]
                    [--runs 1] [--rfc ../../publish/oak-0001.txt]

Each run copies a fixture project and the RFC text into a fresh temp folder,
then asks the agent: "Read the document at <path>. Set up memory for this
project by following it." The RFC sits next to the project, as if the user
pointed the agent at a URL. `atlas` is a logging stub. With bubblewrap, the
suite, the user's global AGENTS.md, and other runs are hidden.

Writes OUT_DIR/<agent>/<fixture>/run<N>/ with project/, stdout.txt,
stub.log, and run.json. Score the result with score_setup.py.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from run_eval import BWRAP, make_stubs  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROMPT = "Read the document at {rfc}. Set up memory for this project by following it."
# Global instruction files that would leak the user's own rules into the run.
GLOBAL_INSTRUCTIONS = [Path.home() / ".agents" / "AGENTS.md"]


def agent_cmd(agent, prompt, work):
    if agent == "pi":
        return ["pi", "-p", "--mode", "json", "--model", "zai/glm-5.3", "--no-session",
                "--no-context-files", "--no-skills", "--no-extensions", "--no-mcp",
                "--no-prompt-templates", "--no-themes", "--no-approve",
                "--tools", "read,bash,edit,write", "--", prompt]
    if agent == "claude":
        return ["claude", "-p", "--output-format", "json", "--no-session-persistence",
                "--dangerously-skip-permissions", "--setting-sources", "project,local",
                "--strict-mcp-config", prompt]
    if agent == "codex":
        return ["codex", "exec", "--json", "--ephemeral", "--skip-git-repo-check",
                "--dangerously-bypass-approvals-and-sandbox", "-C", str(work), prompt]
    raise ValueError(agent)


def run_one(agent, fixture, n, a):
    run_dir = Path(a.out) / agent / fixture / f"run{n}"
    if (run_dir / "run.json").exists():
        return f"skip {run_dir}"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    tmp = Path(tempfile.mkdtemp(prefix="oak-setup-"))
    stubs = Path(tempfile.mkdtemp(prefix="oak-stubs-"))
    work = tmp / "project"
    shutil.copytree(HERE / "fixtures" / fixture, work)
    rfc = tmp / "oak-0001.txt"
    shutil.copy2(a.rfc, rfc)
    rfc_sha = hashlib.sha256(rfc.read_bytes()).hexdigest()[:12]  # the text this run read
    stub_log = stubs / "stub.log"
    stub_log.touch()
    make_stubs(stubs / "bin", stub_log)

    cmd = agent_cmd(agent, PROMPT.format(rfc=rfc), work)
    if BWRAP:
        hide = {ROOT.parent, Path(a.out).resolve()}
        hide = {h for h in hide if not any(o in h.parents for o in hide)}
        wrap = [BWRAP, "--dev-bind", "/", "/", "--die-with-parent"]
        for h in sorted(hide):
            wrap += ["--tmpfs", str(h)]
        for g in GLOBAL_INSTRUCTIONS:
            if g.exists():
                wrap += ["--ro-bind", "/dev/null", str(g.resolve())]
        wrap += ["--tmpfs", "/tmp", "--bind", str(tmp), str(tmp),
                 "--bind", str(stubs), str(stubs), "--chdir", str(work)]
        cmd = wrap + cmd
    env = dict(os.environ, PATH=f"{stubs / 'bin'}:{os.environ['PATH']}")
    t0 = time.monotonic()
    with open(run_dir / "stdout.txt", "w") as out, open(run_dir / "stderr.txt", "w") as err:
        try:
            code = subprocess.run(cmd, cwd=work, env=env, stdout=out, stderr=err,
                                  timeout=a.timeout).returncode
        except subprocess.TimeoutExpired:
            code = "timeout"
    wall = round(time.monotonic() - t0, 1)
    shutil.copytree(work, run_dir / "project", symlinks=True)
    shutil.copy2(stub_log, run_dir / "stub.log")
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.rmtree(stubs, ignore_errors=True)
    if code != 0:
        return f"infra-fail {run_dir} exit={code} (see stderr.txt); rerun to retry"
    (run_dir / "run.json").write_text(json.dumps({
        "agent": agent, "fixture": fixture, "run": n, "exit": code, "wall_s": wall,
        "rfc_sha256": rfc_sha,
        "stub_calls": (run_dir / "stub.log").read_text().splitlines(),
    }, indent=2) + "\n")
    return f"done {run_dir} {wall}s"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--agents", default="pi,claude,codex")
    ap.add_argument("--fixtures", default="empty,messy")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--rfc", default=str(ROOT.parent / "publish" / "oak-0001.txt"))
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()
    for agent in a.agents.split(","):
        for fixture in a.fixtures.split(","):
            for n in range(1, a.runs + 1):
                print(run_one(agent, fixture, n, a), flush=True)


if __name__ == "__main__":
    main()
