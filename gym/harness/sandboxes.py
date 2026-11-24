"""Shared sandbox and multi-agent execution helpers for the OAK Gym."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

HARNESS_DIR = Path(__file__).resolve().parent
GYM_DIR = HARNESS_DIR.parent
OAK_ROOT = GYM_DIR.parent
SUBSTRATES_DIR = GYM_DIR / "substrates"
SPEC_CURRENT = OAK_ROOT / "publish/oak-0001.txt"
SPEC_V04 = OAK_ROOT / "publish/oak-0001-v0.4.txt"

BWRAP = "/usr/bin/bwrap"
NODE_BIN = "/home/agent/.local/share/mise/installs/node/24.18.0/bin/node"
PI_BIN = "/home/agent/oak-tools/node_modules/.bin/pi"

SUPPORTED_AGENTS = (
    "claude_opus_5_5",
    "codex_gpt_6_2_sol",
    "agy_gemini_4_neon",
    "pi_glm_5_4",
    "pi_glm_5_3",
)


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=check, capture_output=True, text=True
    )


def ensure_code_venv(cache_root: Path | None = None) -> Path:
    """Ensure a Python venv with pytest and freezegun exists outside OAK_ROOT."""
    existing = Path("/tmp/itsdangerous-venv/bin/pytest")
    if existing.is_file():
        return existing.parent
    venv_dir = (cache_root or (Path(tempfile.gettempdir()) / "oak-gym-venvs/itsdangerous")).resolve()
    if not (venv_dir / "bin/pytest").is_file():
        venv_dir.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["python3", "-m", "venv", str(venv_dir)], check=True)
        subprocess.run(
            [str(venv_dir / "bin/pip"), "install", "-q", "pytest", "freezegun"],
            check=True,
        )
    return venv_dir / "bin"


def make_pi_agent_dir() -> Path:
    """Create a temporary writable Pi config directory with Z.ai auth & models."""
    d = Path(tempfile.mkdtemp(prefix="/tmp/oak-pi-cfg-"))
    os.chmod(d, 0o700)
    for src in (Path("/home/agent/.config/oak-pi-agent/auth.json"), Path.home() / ".pi/agent/auth.json"):
        if src.is_file():
            shutil.copy2(src, d / "auth.json")
            break
    for msrc in (Path.home() / ".pi/agent/models.json", Path("/home/agent/.config/oak-pi-agent/models.json")):
        if msrc.is_file():
            shutil.copy2(msrc, d / "models.json")
            break
    return d


def build_agent_cmd(agent_id: str, work_dir: Path, prompt: str) -> list[str]:
    if agent_id == "claude_opus_5_5":
        return [
            "/home/agent/.local/bin/claude",
            "-p",
            "--output-format",
            "json",
            "--no-session-persistence",
            "--dangerously-skip-permissions",
            "--setting-sources",
            "project,local",
            "--strict-mcp-config",
            "--model",
            "claude-opus-5-5",
            prompt,
        ]
    if agent_id == "codex_gpt_6_2_sol":
        return [
            "/home/agent/.local/share/mise/shims/codex",
            "exec",
            "--json",
            "--ephemeral",
            "--skip-git-repo-check",
            "--dangerously-bypass-approvals-and-sandbox",
            "-m",
            "gpt-6.2-sol",
            "-C",
            str(work_dir),
            prompt,
        ]
    if agent_id == "agy_gemini_4_neon":
        return [
            "/home/agent/.local/bin/agy",
            "--dangerously-skip-permissions",
            "--disable-slash-commands",
            "--output-format",
            "json",
            "--model",
            "gemini-4-neon-medium",
            f"-p={prompt}",
        ]
    if agent_id in ("pi_glm_5_4", "pi_glm_5_3"):
        model = "glm-5.4" if agent_id == "pi_glm_5_4" else "glm-5.3"
        return [
            NODE_BIN,
            PI_BIN,
            "-p",
            "--mode",
            "json",
            "--no-session",
            "--no-extensions",
            "--no-mcp",
            "--no-skills",
            "--no-prompt-templates",
            "--no-themes",
            "--no-approve",
            "--provider",
            "zai",
            "--model",
            model,
            "--thinking",
            "low",
            "--tools",
            "read,bash,edit,write",
            "--",
            prompt,
        ]
    raise ValueError(f"Unsupported agent_id: {agent_id}")


def run_sandboxed_agent(
    agent_id: str,
    source_dir: Path,
    prompt: str,
    trial_out: Path,
    hide_dirs: list[Path] | None = None,
    extra_path_dirs: list[Path] | None = None,
    timeout: int = 540,
) -> dict:
    """Run one agent CLI inside bwrap hiding OAK_ROOT, output dirs, and global AGENTS.md."""
    trial_out = trial_out.resolve()
    trial_out.mkdir(parents=True, exist_ok=True)
    tmp_parent = Path(tempfile.mkdtemp(prefix="/tmp/oak-gym-work-"))
    work = tmp_parent / "repo"
    shutil.copytree(source_dir, work)

    pi_cfg = make_pi_agent_dir() if agent_id.startswith("pi_") else None
    try:
        inner_cmd = build_agent_cmd(agent_id, work, prompt)
        to_hide = {OAK_ROOT.resolve(), trial_out.parent.resolve()}
        for hd in hide_dirs or []:
            to_hide.add(hd.resolve())
        # Collapse child paths if a parent path is already hidden
        to_hide = {h for h in to_hide if h.exists() and not any(p in h.parents for p in to_hide)}

        wrap = [BWRAP, "--dev-bind", "/", "/", "--die-with-parent"]
        for h in sorted(to_hide):
            wrap.extend(["--tmpfs", str(h)])
        global_agents = Path.home() / ".agents/AGENTS.md"
        if global_agents.exists():
            wrap.extend(["--ro-bind", "/dev/null", str(global_agents.resolve())])
        wrap.extend(["--bind", str(tmp_parent), str(tmp_parent), "--chdir", str(work)])
        if pi_cfg is not None:
            wrap.extend(["--bind", str(pi_cfg), str(pi_cfg)])

        env = dict(os.environ)
        path_parts = [str(p) for p in (extra_path_dirs or [])] + [
            "/home/agent/.local/bin",
            "/home/agent/.local/share/mise/shims",
            env.get("PATH", ""),
        ]
        env["PATH"] = ":".join(p for p in path_parts if p)
        if pi_cfg is not None:
            env["PI_CODING_AGENT_DIR"] = str(pi_cfg)

        (trial_out / "prompt.txt").write_text(prompt)
        t0 = time.monotonic()
        timed_out = False
        with (trial_out / "stdout.log").open("w") as out_f, (trial_out / "stderr.log").open("w") as err_f:
            try:
                proc = subprocess.run(wrap + inner_cmd, cwd=work, env=env, stdout=out_f, stderr=err_f, timeout=timeout)
                code = proc.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                code = -9
        wall = round(time.monotonic() - t0, 2)
        shutil.copytree(work, trial_out / "project")
        meta = {"agent_id": agent_id, "exit_code": code, "timed_out": timed_out, "wall_seconds": wall}
        (trial_out / "run_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        return meta
    finally:
        shutil.rmtree(tmp_parent, ignore_errors=True)
        if pi_cfg is not None:
            shutil.rmtree(pi_cfg, ignore_errors=True)


def replace_working_tree(src: Path, dst_git_repo: Path) -> None:
    for p in list(dst_git_repo.iterdir()):
        if p.name == ".git":
            continue
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
    for p in src.iterdir():
        if p.name == ".git":
            continue
        if p.is_dir():
            shutil.copytree(p, dst_git_repo / p.name)
        else:
            shutil.copy2(p, dst_git_repo / p.name)
