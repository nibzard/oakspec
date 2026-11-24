#!/usr/bin/env python3
"""Build the condition variants of every case fixture.

usage: make_variants.py CASES_DIR OUT_DIR

OUT_DIR/<condition>/<case>/knowledge/... is written for each condition:

  oak          canonical fixtures
  plain        oak block removed; other frontmatter kept
  sidecar      oak block moved to <file>.oak.json
  prose        oak block rewritten as a sentence at the top of the body
  oak+guide    oak, plus OAK-GUIDE.md in the knowledge root
  plain+guide  plain, plus OAK-GUIDE.md (without its own oak block)
  prose+guide  prose, plus WRITING-GUIDE.md (same advice, no metadata)

The main experiment uses plain (A), prose+guide (B), and oak+guide (C).
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oaklib  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OAK_GUIDE = ROOT / "OAK-GUIDE.md"
WRITING_GUIDE = ROOT / "WRITING-GUIDE.md"

# condition -> (how to convert fixtures, guide file or None)
CONDITIONS = {
    "oak": ("oak", None),
    "plain": ("plain", None),
    "sidecar": ("sidecar", None),
    "prose": ("prose", None),
    "oak+guide": ("oak", OAK_GUIDE),
    "plain+guide": ("plain", OAK_GUIDE),
    "prose+guide": ("prose", WRITING_GUIDE),
}
KIND_WORDS = {"record": "Record", "reference": "Reference note", "spec": "Specification"}


def md_links(refs):
    if isinstance(refs, str):
        refs = [refs]
    return ", ".join(f"[{r}]({r})" for r in refs)


def prose_line(oak):
    """Say what the oak block says, as one plain paragraph."""
    kind = oak.get("kind")
    head = KIND_WORDS.get(kind, f"Kind: {kind}")
    if oak.get("at"):
        head += f" of an event on {oak['at']}"
    parts = [head + "."]
    if oak.get("as_of"):
        parts.append(f"As of {oak['as_of']}.")
    if oak.get("origin"):
        parts.append(f"Origin: {oak['origin']}.")
    if oak.get("status"):
        parts.append(f"Status: {oak['status']}.")
    if oak.get("superseded_by"):
        parts.append(f"Superseded by {md_links(oak['superseded_by'])}.")
    if oak.get("sources"):
        parts.append(f"Sources: {md_links(oak['sources'])}.")
    if oak.get("links"):
        parts.append(f"Related: {md_links(oak['links'])}.")
    return " ".join(parts)


def convert(src: Path, dst: Path, mode: str):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix != ".md" or mode == "oak":
        shutil.copy2(src, dst)
        return
    meta, body = oaklib.split(src.read_text())
    if not meta or "oak" not in meta:
        shutil.copy2(src, dst)
        return
    oak = meta.pop("oak")
    if mode == "prose":
        body = prose_line(oak) + "\n\n" + body
    dst.write_text(oaklib.join(meta, body))
    if mode == "sidecar":
        side = oaklib.sidecar_path(dst)
        side.write_text(json.dumps({"oak": oak}, indent=2, default=str) + "\n")


def main(cases_dir, out_dir):
    cases_dir, out_dir = Path(cases_dir), Path(out_dir)
    for case in sorted(p for p in cases_dir.iterdir() if p.is_dir()):
        kdir = case / "knowledge"
        for cond, (mode, guide) in CONDITIONS.items():
            target = out_dir / cond / case.name
            if target.exists():
                shutil.rmtree(target)
            for f in kdir.rglob("*"):
                if f.is_file():
                    convert(f, target / "knowledge" / f.relative_to(kdir), mode)
            if guide:
                convert(guide, target / "knowledge" / guide.name, mode)
            shutil.copy2(case / "case.yaml", target / "case.yaml")
    print(f"wrote {', '.join(CONDITIONS)} variants to {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
