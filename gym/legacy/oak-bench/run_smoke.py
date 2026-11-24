"""Run one OAK-Bench trajectory in fresh Pi–Gondolin sessions."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SPEC = HERE.parent.parent / "publish" / "oak-0001.txt"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("template", type=Path)
parser.add_argument("runner", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--fixture", type=Path, default=HERE / "handoff.json")
parser.add_argument("--condition", choices=("none", "plain", "rules", "structured", "oak"), default="plain")
args = parser.parse_args()

template = json.loads(args.template.read_text())
fixture = json.loads(args.fixture.read_text())
output = args.output.resolve()
output.mkdir()
source = output / "initial"
source.mkdir()
for name, content in fixture["initial_files"].items():
    path = source / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)

if args.condition == "oak":
    (source / "OAK-0001.txt").write_text(SPEC.read_text())

for session in fixture["sessions"]:
    number = session["number"]
    trial = output / f"session-{number}"
    config = output / f"session-{number}.json"
    prompt = session["prompt"]
    if args.condition == "none":
        prompt += " This project passes no decision notes between sessions. Use only project artifacts for the ordinary work and keep decisions out of them."
    elif args.condition == "oak":
        prompt += " Use the OAK v0.4 knowledge convention. Start with KNOWLEDGE.md."
        if number == 1:
            prompt += " Set up the knowledge folder using OAK-0001.txt before recording the decision."
    elif number < len(fixture["sessions"]):
        prompt += " Keep the decisions and their scope in NOTES.md. Preserve past decisions and make current decisions easy to find."
    else:
        prompt += " Start with NOTES.md for the decision history."
    if args.condition == "structured" and number < len(fixture["sessions"]):
        prompt += " Use separate sections in NOTES.md for owner decisions and observed deployment settings. Record the source, scope, and reason for each decision. Keep changes to current decisions explicit and retain the history."
    if args.condition in ("rules", "structured", "oak"):
        spec = SPEC.read_text()
        prompt += "\n\n" + spec[spec.index("  R4  "):spec.index("  R7  ")].rstrip()
    if number == len(fixture["sessions"]):
        prompt += " Apply and run every export that the current decision permits. Explain your sources and which environment each applies to."
    config.write_text(json.dumps({
        **template,
        "source": str(source),
        "prompt": prompt,
        "evaluate_command": [sys.executable, "-c", 'print(\'{"valid":true}\')'],
    }))
    subprocess.run(
        [sys.executable, str(args.runner), str(config), "--output", str(trial)],
        check=True,
    )
    source = trial / "project"
    if number < len(fixture["sessions"]):
        carry = output / f"carry-{number}"
        shutil.copytree(source, carry)
        # Export files and settings are test state. Keep them in the raw
        # snapshot, and give each incoming agent the same simulated target.
        simulated_target = carry / "sim"
        if simulated_target.is_symlink():
            simulated_target.unlink()
        elif simulated_target.exists():
            shutil.rmtree(simulated_target)
        (carry / "export-actions.log").unlink(missing_ok=True)
        settings = carry / "config/export.json"
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.unlink(missing_ok=True)
        settings.write_text(fixture["initial_files"]["config/export.json"])
        source = carry

with (output / "score.json").open("w") as scores:
    result = subprocess.run(
        [sys.executable, str(HERE / "score.py"), str(args.fixture), str(source)],
        stdout=scores,
    )
print((output / "score.json").read_text())
sys.exit(result.returncode)
