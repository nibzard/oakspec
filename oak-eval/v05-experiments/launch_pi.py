#!/usr/bin/env python3
"""Unprivileged launcher for Pi with the Gondolin VM extension.

Always passes --no-context-files so host ~/.agents/AGENTS.md never leaks into
trials. When --context-files=project is requested and {project}/AGENTS.md
exists, appends ONLY {project}/AGENTS.md to the system prompt.
"""
import argparse
import os
from pathlib import Path

NODE = "/home/agent/.local/share/mise/installs/node/24.18.0/bin/node"
PI = "/home/agent/oak-tools/node_modules/.bin/pi"
GONDOLIN_EXT = "/home/agent/oak-tools/pi-gondolin.ts"
AGENT_DIR = "/home/agent/.config/oak-pi-agent"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--context-files", choices=("none", "project"), default="none")
    ap.add_argument("--provider", default="zai")
    ap.add_argument("--model", default="glm-5.3")
    ap.add_argument("--thinking", default="low")
    ap.add_argument("prompt")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    env = dict(os.environ)
    env["PI_CODING_AGENT_DIR"] = AGENT_DIR
    env["PATH"] = f"/home/agent/.local/share/mise/installs/node/24.18.0/bin:/usr/local/bin:/usr/bin:/bin:{env.get('PATH', '')}"

    cmd = [
        NODE,
        PI,
        "-p",
        "--mode",
        "json",
        "--no-session",
        "--no-extensions",
        "--no-mcp",
        "--no-skills",
        "--no-prompt-templates",
        "--no-themes",
        "--no-context-files",
    ]
    if args.context_files == "project" and (project / "AGENTS.md").is_file():
        agents_text = (project / "AGENTS.md").read_text()
        cmd.extend([
            "--append-system-prompt",
            f"# Project Context (/workspace/AGENTS.md)\n\n{agents_text}",
        ])
    cmd.extend([
        "--provider",
        args.provider,
        "--model",
        args.model,
        "--thinking",
        args.thinking,
        "-e",
        GONDOLIN_EXT,
        args.prompt,
    ])

    os.chdir(project)
    os.execve(NODE, cmd, env)


if __name__ == "__main__":
    main()
