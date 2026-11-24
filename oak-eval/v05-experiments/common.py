"""Shared utilities for OAK v0.5 Pi + Gondolin experiments."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
RUNNER = REPO_ROOT / ".agents/skills/pi-gondolin-experiments/scripts/run_trial.py"
LAUNCHER = HERE / "launch_pi.py"
SPEC_V04 = REPO_ROOT / "publish/oak-0001-v0.4.txt"
SPEC_V05 = REPO_ROOT / "publish/oak-0001.txt"
DEFAULT_MODEL = os.environ.get("OAK_EVAL_MODEL", "glm-5.3")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_files(root: Path, files: dict[str, str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for rel, content in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)


def agent_command(context_files: str = "none", model: str | None = None) -> list[str]:
    return [
        sys.executable,
        str(LAUNCHER),
        "--project",
        "{project}",
        "--context-files",
        context_files,
        "--model",
        model or DEFAULT_MODEL,
        "{prompt}",
    ]


def parse_pi_metrics(stdout_path: Path) -> dict:
    tool_calls = 0
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    turns = 0
    if not stdout_path.is_file():
        return {"turns": 0, "tool_calls": 0, "total_tokens": 0}
    for line in stdout_path.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "turn_end":
            turns += 1
            tool_calls += len(ev.get("toolResults") or [])
            usage = (ev.get("message") or {}).get("usage") or {}
            input_tokens += int(usage.get("input") or 0) + int(usage.get("cacheRead") or 0)
            output_tokens += int(usage.get("output") or 0)
            total_tokens += int(usage.get("totalTokens") or 0)
    return {
        "turns": turns,
        "tool_calls": tool_calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def run_trial(
    source: Path,
    prompt: str,
    output_dir: Path,
    evaluate_command: list[str] | None = None,
    context_files: str = "none",
    model: str | None = None,
    timeout_seconds: int = 300,
) -> dict:
    output_dir = output_dir.resolve()
    cfg_path = output_dir.parent / f"{output_dir.name}.config.json"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    if evaluate_command is None:
        evaluate_command = [sys.executable, "-c", 'print(\'{"valid": true}\')']
    cfg = {
        "source": str(source.resolve()),
        "prompt": prompt,
        "timeout_seconds": timeout_seconds,
        "agent_command": agent_command(context_files=context_files, model=model),
        "evaluate_command": evaluate_command,
    }
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n")
    subprocess.run(
        [sys.executable, str(RUNNER), str(cfg_path), "--output", str(output_dir)],
        check=False,
        capture_output=True,
        text=True,
    )
    res = json.loads((output_dir / "result.json").read_text())
    res["pi_metrics"] = parse_pi_metrics(output_dir / "agent.stdout")
    (output_dir / "result.json").write_text(json.dumps(res, indent=2) + "\n")
    return res
