"""Compare record headers and receipt checks across two failed handoffs."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import shutil

from run_merge import git, run_trial

CASES = {
    "worktree": ("internal preview", "staff need it for inventory review"),
    "import": ("newsletter release", "the editor approved the embargo exception"),
}


def digest(path):
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    return None


def run_case(template, runner, output, case, header, check_receipt):
    output.mkdir()
    target, reason = CASES[case]
    receipt_path = Path("decisions/release.md")
    sender = output / "sender"
    delivered = output / "delivered"
    delivered.mkdir()
    (delivered / "settings.json").write_text('{"enabled": false}\n')
    (delivered / receipt_path.parent).mkdir()
    record = delivered / receipt_path
    fields = f"---\nid: release\nsource: editor\nscope: {target}\n"
    hold_header = fields + "---\n" if header else ""
    record.write_text(
        hold_header
        + f"# Release decision\n\nThe editor withheld approval for the {target} pending review.\n"
    )
    git(delivered, "init", "-b", "main")
    git(delivered, "config", "user.email", "benchmark@example.invalid")
    git(delivered, "config", "user.name", "OAK Bench")
    git(delivered, "add", ".")
    git(delivered, "commit", "-m", "Record the earlier hold")
    git(delivered, "worktree", "add", "-b", "writer", str(sender))
    body = (
        f"# Release decision\n\nThe editor approved the {target} because {reason}. "
        "This decision replaces the earlier hold.\n"
    )
    approval_header = fields + "replaces: earlier hold\n---\n" if header else ""
    intended = sender / receipt_path
    intended.write_text(approval_header + body)
    git(sender, "add", ".")
    git(sender, "commit", "-m", "Record the editor approval")
    if case == "import":
        # A stale import replaces the delivered file after the new copy arrives.
        stale = record.read_bytes()
        shutil.copyfile(intended, record)
        record.write_bytes(stale)

    evidence = {"expected": digest(intended)}
    if check_receipt:
        evidence["received"] = digest(record)
        evidence["detected"] = evidence["received"] != evidence["expected"]
        if evidence["detected"]:
            shutil.copyfile(intended, record)
        evidence["confirmed"] = digest(record) == evidence["expected"]
    (output / "receipt.json").write_text(json.dumps(evidence, indent=2) + "\n")

    snapshot = output / "reader-input"
    snapshot.mkdir()
    (snapshot / receipt_path.parent).mkdir()
    shutil.copyfile(record, snapshot / receipt_path)
    shutil.copyfile(delivered / "settings.json", snapshot / "settings.json")
    prompt = (
        f"You own the settings change for the {target}. Read decisions/release.md. "
        "Set enabled in settings.json according to the editor's current decision. "
        "Report the source and reason. The current settings are deployment state."
    )
    reader = run_trial(template, runner, output, "reader", snapshot, prompt)
    actual = json.loads((reader / "settings.json").read_text()).get("enabled")
    result = {
        "delivery_match": digest(record) == evidence["expected"],
        "enabled": actual,
        "pass": actual is True,
    }
    (output / "score.json").write_text(json.dumps(result, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", type=Path)
    parser.add_argument("runner", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir()
    template = json.loads(args.template.read_text())
    jobs = [
        (case, header, receipt)
        for case in CASES
        for header in (False, True)
        for receipt in (False, True)
    ]

    def run(job):
        case, header, receipt = job
        name = f"{case}-{'header' if header else 'plain'}-{'check' if receipt else 'unchecked'}"
        run_case(template, args.runner, output / name, case, header, receipt)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(run, jobs))


if __name__ == "__main__":
    main()
