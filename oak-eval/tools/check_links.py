#!/usr/bin/env python3
"""Check an OAK knowledge directory after an agent has edited it.

usage: check_links.py KNOWLEDGE_DIR [--baseline FIXTURE_DIR]
                      [--unchanged PATH]... [--unchanged-body PATH]...
                      [--require-key PATH:KEY]... [--forbid-path PATH]...

Always checked:
  - every local reference in oak links/sources/superseded_by resolves,
    whether the oak block is in frontmatter or in a `<file>.oak.json` sidecar
  - every local Markdown body link resolves
  - no file has both an embedded oak block and a sidecar (RFC §7.4)
  - every sidecar sits next to an existing file
  - every .md file that had an oak block in the baseline and still exists
    still has one, with the same kind

Use the knowledge directory of the same condition as the baseline (for
example build/plain/05-correct-preference/knowledge), not the canonical
fixture.

--unchanged-body ignores Markdown links, so a rename may update them.
Exit status is 1 if any check fails.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oaklib  # noqa: E402


def resolve(base_file: Path, ref: str) -> Path:
    return (base_file.parent / ref.split("#", 1)[0]).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("knowledge")
    ap.add_argument("--baseline")
    ap.add_argument("--unchanged", action="append", default=[])
    ap.add_argument("--unchanged-body", action="append", default=[])
    ap.add_argument("--require-key", action="append", default=[])
    ap.add_argument("--forbid-path", action="append", default=[])
    a = ap.parse_args()

    root = Path(a.knowledge).resolve()
    base = Path(a.baseline).resolve() if a.baseline else None
    errors = []

    for f in sorted(root.rglob("*.md")):
        rel = f.relative_to(root)
        _, body, oak, conflict = oaklib.load(f)
        if conflict:
            errors.append(f"{rel}: oak block both embedded and in sidecar")
        for ref in oaklib.oak_refs({"oak": oak}):
            if oaklib.is_local(ref) and not resolve(f, ref).exists():
                errors.append(f"{rel}: oak reference does not resolve: {ref}")
        for ref in oaklib.body_links(body):
            if oaklib.is_local(ref) and not resolve(f, ref).exists():
                errors.append(f"{rel}: body link does not resolve: {ref}")
    for side in sorted(root.rglob("*" + oaklib.SIDECAR_SUFFIX)):
        owner = side.with_name(side.name[: -len(oaklib.SIDECAR_SUFFIX)])
        if not owner.exists():
            errors.append(f"{side.relative_to(root)}: sidecar without its file")

    if base:
        for bf in sorted(base.rglob("*.md")):
            rel = bf.relative_to(base)
            boak = oaklib.load(bf)[2]
            cur = root / rel
            if not (boak and cur.exists()):
                continue
            oak = oaklib.load(cur)[2]
            if not oak:
                errors.append(f"{rel}: oak block lost")
            elif oak.get("kind") != boak.get("kind"):
                errors.append(f"{rel}: kind changed")

    def need_base(flag):
        if not base:
            sys.exit(f"{flag} requires --baseline")

    for p in a.unchanged:
        need_base("--unchanged")
        if not (root / p).exists() or (root / p).read_bytes() != (base / p).read_bytes():
            errors.append(f"{p}: modified or missing (must be unchanged)")
    for p in a.unchanged_body:
        need_base("--unchanged-body")
        if not (root / p).exists():
            errors.append(f"{p}: missing")
            continue
        _, b1 = oaklib.split((root / p).read_text())
        _, b0 = oaklib.split((base / p).read_text())
        if oaklib.strip_links(b1) != oaklib.strip_links(b0):
            errors.append(f"{p}: body text changed")
    for spec in a.require_key:
        p, key = spec.split(":", 1)
        if not (root / p).exists():
            errors.append(f"{p}: missing (required key {key})")
            continue
        meta, _ = oaklib.split((root / p).read_text())
        if not meta or key not in meta:
            errors.append(f"{p}: frontmatter key '{key}' missing")
    for p in a.forbid_path:
        for gone in (root / p, oaklib.sidecar_path(root / p)):
            if gone.exists():
                errors.append(f"{gone.relative_to(root)}: should not exist")
        for f in root.rglob("*.md"):
            _, body, oak, _ = oaklib.load(f)
            for ref in oaklib.oak_refs({"oak": oak}) + oaklib.body_links(body):
                if oaklib.is_local(ref) and resolve(f, ref) == (root / p).resolve():
                    errors.append(f"{f.relative_to(root)}: still points to {p}")

    for e in errors:
        print("FAIL", e)
    print("OK" if not errors else f"{len(errors)} problem(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
