"""Run two independent decision writers, a merge, and a fresh reader."""
import argparse
import concurrent.futures
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
LAYOUTS = {
    "shared": "Keep all decisions in NOTES.md. Use separate sections for owner decisions and observed settings. Record the source, scope, reason, and history.",
    "files": "Create a new Markdown file under decisions/ for this decision. Record its source, scope, reason, and history in prose. Keep observed settings separate.",
    "oak": "Follow OAK-0001.txt. Create a new dated decision record under knowledge/records/. Use its prescribed metadata. Leave shared entry points alone.",
}


def git(repo, *args, check=True):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=check, capture_output=True, text=True
    )


def run_trial(template, runner, evidence, name, source, prompt):
    config = evidence / f"{name}.json"
    output = evidence / name
    config.write_text(json.dumps({
        **template,
        "source": str(source),
        "prompt": prompt,
        "evaluate_command": [sys.executable, "-c", 'print(\'{"valid":true}\')'],
    }))
    subprocess.run(
        [sys.executable, str(runner), str(config), "--output", str(output)],
        check=True,
    )
    return output / "project"


def copy_files(source, target):
    for path in source.iterdir():
        if path.name == ".git":
            continue
        if path.is_dir():
            shutil.copytree(path, target / path.name, dirs_exist_ok=True)
        else:
            shutil.copy2(path, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", type=Path)
    parser.add_argument("runner", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("layout", choices=LAYOUTS)
    args = parser.parse_args()
    template = json.loads(args.template.read_text())
    evidence = args.output.resolve()
    evidence.mkdir()
    seed = evidence / "seed"
    seed.mkdir()
    (seed / "README.md").write_text(
        "# Harbor reports\n\nThis is a simulated weekly report project. "
        "Decisions are recorded in the project notes.\n"
    )
    (seed / "settings.json").write_text('{"internal": false, "public": false}\n')
    if args.layout == "shared":
        (seed / "NOTES.md").write_text("# Notes\n\n## Owner decisions\n\n## Observed settings\n")
    if args.layout == "oak":
        (seed / "OAK-0001.txt").write_text((HERE.parents[1] / "publish/oak-0001.txt").read_text())
        (seed / "KNOWLEDGE.md").write_text("# Knowledge\n\nRead dated decision records under knowledge/records/.\n")
    layout = LAYOUTS[args.layout]
    decisions = {
        "internal": "Avery, the project owner, approved the internal weekly report because the staff need it for inventory review. Approval covers the internal target only.",
        "public": "Avery, the project owner, rejected the public weekly report because the catalog contains unpublished inventory. This decision covers the public target only.",
    }

    def write(item):
        name, decision = item
        prompt = f"Record this new decision for a future maintainer. {decision} {layout} Leave project settings unchanged; this task is to record the decision."
        return run_trial(template, args.runner, evidence, name, seed, prompt)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        writers = dict(zip(decisions, pool.map(write, decisions.items())))

    repo = evidence / "merged"
    shutil.copytree(seed, repo)
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "benchmark@example.invalid")
    git(repo, "config", "user.name", "OAK Bench")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "Add the seed")
    for name, project in writers.items():
        git(repo, "switch", "-c", name, "main")
        copy_files(project, repo)
        git(repo, "add", ".")
        git(repo, "commit", "--allow-empty", "-m", f"Record the {name} decision")
    git(repo, "switch", "main")
    git(repo, "merge", "--ff-only", "internal")
    merge = git(repo, "merge", "--no-edit", "public", check=False)
    conflicts = git(repo, "diff", "--name-only", "--diff-filter=U").stdout.splitlines()
    if merge.returncode:
        if not conflicts:
            raise RuntimeError(merge.stderr or merge.stdout)
        snapshot = evidence / "conflict-input"
        snapshot.mkdir()
        copy_files(repo, snapshot)
        resolved = run_trial(template, args.runner, evidence, "resolver", snapshot,
                             "Resolve the conflict markers. Keep all owner decisions and their sources, scopes, and reasons. Leave settings unchanged.")
        copy_files(resolved, repo)
        git(repo, "add", ".")
        git(repo, "commit", "-m", "Resolve the decisions merge")

    snapshot = evidence / "reader-input"
    snapshot.mkdir()
    copy_files(repo, snapshot)
    reader = run_trial(template, args.runner, evidence, "reader", snapshot,
                       "You own the settings change. Set each target in settings.json to true if the owner approved it and false otherwise. Report the reason and cite the notes for each target.")
    actual = json.loads((reader / "settings.json").read_text())
    result = {
        "conflicts": conflicts,
        "settings": actual,
        "pass": isinstance(actual, dict) and actual.get("internal") is True and actual.get("public") is False,
    }
    (evidence / "score.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result)


if __name__ == "__main__":
    main()
