#!/usr/bin/env python3
"""Deterministic OAK-0001 v0.5 conformance and self-check tool (Section 5.1 & 10).

Checks tool-conformant OAK folders (YAML frontmatter or adjacent <file>.oak.json
sidecar) for:
  C1  Valid kind (record, reference, spec) when oak metadata is present
  C2  Records carry valid ISO date in `at`; `at` is never set on non-records
  C3  `as_of` only on reference/spec (valid ISO date)
  C5  `status: superseded` has a resolving `superseded_by` target
  C6  All local paths in `sources`, `links`, `superseded_by`, and Markdown body
      links resolve to an existing file or folder
  C9  If `index.md` exists, every Markdown resource is reachable via file or
      folder links
  C10 Project root has `AGENTS.md` or `CLAUDE.md` pointing to the knowledge folder
  Plus closed-set validation on `origin` (user, agent, inferred, external) and
  detection of conflicting embedded + sidecar `oak` metadata.
"""
import argparse
import json
from pathlib import Path
import re
import sys
import yaml

FM_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.S)
CODE_RE = re.compile(r"^```.*?^```|^(?: {4}|\t).*?$|`[^`\n]*`", re.S | re.M)
MD_LINK_RE = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}.*)?$")

VALID_KINDS = {"record", "reference", "spec"}
VALID_ORIGINS = {"user", "agent", "inferred", "external"}
REF_FIELDS = ("links", "sources", "superseded_by")
SIDECAR_SUFFIX = ".oak.json"


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    m = FM_RE.match(text)
    if not m:
        return None, text
    data = yaml.safe_load(m.group(1)) or {}
    return (data if isinstance(data, dict) else {}), text[m.end():]


def load_resource(path: Path) -> tuple[dict | None, str, dict | None, bool]:
    meta, body = split_frontmatter(path.read_text(errors="replace"))
    oak = (meta or {}).get("oak") if isinstance(meta, dict) else None
    side = path.with_name(path.name + SIDECAR_SUFFIX)
    conflict = False
    if side.is_file():
        side_data = json.loads(side.read_text(errors="replace")) or {}
        side_oak = side_data.get("oak") if isinstance(side_data, dict) else None
        conflict = oak is not None and side_oak is not None
        if oak is None:
            oak = side_oak
    return meta, body, oak, conflict


def oak_refs(oak: dict | None) -> list[str]:
    if not isinstance(oak, dict):
        return []
    out = []
    for k in REF_FIELDS:
        v = oak.get(k)
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, list):
            out.extend(x for x in v if isinstance(x, str))
    return out


def body_links(body: str) -> list[str]:
    return MD_LINK_RE.findall(CODE_RE.sub("", body))


def is_local(ref: str) -> bool:
    return "://" not in ref and not ref.startswith(("mailto:", "#"))


def resolve_ref(base_file: Path, ref: str) -> Path:
    clean = ref.split("#", 1)[0]
    return (base_file.parent / clean).resolve()


def check_knowledge_dir(knowledge_dir: Path, project_root: Path | None = None) -> dict:
    root = knowledge_dir.resolve()
    proj = (project_root or root.parent).resolve()
    errors: list[str] = []

    if not root.is_dir():
        return {"valid": False, "errors": [f"knowledge folder not found: {root}"], "resource_count": 0}

    md_files = sorted(root.rglob("*.md"))
    resources = [f for f in md_files if f.name != "index.md"]
    loaded = {f: load_resource(f) for f in md_files}

    for f in md_files:
        rel = f.relative_to(root)
        _, body, oak, conflict = loaded[f]
        if conflict:
            errors.append(f"{rel}: has both frontmatter oak block and {SIDECAR_SUFFIX} sidecar")
        if oak is not None:
            if not isinstance(oak, dict):
                errors.append(f"{rel}: oak metadata must be a mapping")
                continue
            kind = oak.get("kind")
            if kind not in VALID_KINDS:
                errors.append(f"{rel}: C1 invalid or missing kind {kind!r}")
            origin = oak.get("origin")
            if origin is not None and origin not in VALID_ORIGINS:
                errors.append(f"{rel}: invalid origin {origin!r} (must be one of {sorted(VALID_ORIGINS)} or omitted)")
            at_val = oak.get("at")
            as_of_val = oak.get("as_of")
            if at_val is not None:
                if kind != "record":
                    errors.append(f"{rel}: C2 'at' is only for records (found on {kind!r})")
                elif not ISO_DATE_RE.match(str(at_val)):
                    errors.append(f"{rel}: C2 'at' is not ISO 8601 date: {at_val!r}")
            if as_of_val is not None:
                if kind == "record":
                    errors.append(f"{rel}: C3 'as_of' is not allowed on records")
                elif not ISO_DATE_RE.match(str(as_of_val)):
                    errors.append(f"{rel}: C3 'as_of' is not ISO 8601 date: {as_of_val!r}")
            if oak.get("status") == "superseded":
                sup = oak.get("superseded_by")
                if not sup or (is_local(str(sup)) and not resolve_ref(f, str(sup)).exists()):
                    errors.append(f"{rel}: C5 superseded resource missing valid superseded_by ({sup!r})")

        for ref in oak_refs(oak if isinstance(oak, dict) else None):
            if is_local(ref) and not resolve_ref(f, ref).exists():
                errors.append(f"{rel}: C6 oak path does not resolve: {ref}")
        for ref in body_links(body):
            if is_local(ref) and not resolve_ref(f, ref).exists():
                errors.append(f"{rel}: C6 Markdown link does not resolve: {ref}")

    for side in sorted(root.rglob("*" + SIDECAR_SUFFIX)):
        owner = side.with_name(side.name[: -len(SIDECAR_SUFFIX)])
        if not owner.exists():
            errors.append(f"{side.relative_to(root)}: orphan sidecar without owner file")

    # C9 reachability from index.md via file or folder links
    idx = root / "index.md"
    unreachable: list[str] = []
    if idx.is_file():
        seen_files: set[Path] = set()
        seen_dirs: set[Path] = set()
        todo: list[Path] = [idx.resolve()]
        while todo:
            cur = todo.pop()
            if not cur.exists():
                continue
            if cur.is_dir():
                if cur in seen_dirs:
                    continue
                seen_dirs.add(cur)
                todo.extend(sorted(p.resolve() for p in cur.rglob("*.md")))
                continue
            if cur in seen_files or cur.suffix != ".md":
                continue
            seen_files.add(cur)
            _, body, oak, _ = loaded.get(cur) or load_resource(cur)
            for ref in body_links(body) + oak_refs(oak if isinstance(oak, dict) else None):
                if is_local(ref):
                    todo.append(resolve_ref(cur, ref))
        for r in resources:
            if r.resolve() not in seen_files:
                unreachable.append(str(r.relative_to(root)))
        if unreachable:
            errors.append(f"C9 unreachable from index.md: {unreachable}")

    # C10 instruction file pointer
    instr_files = [proj / name for name in ("AGENTS.md", "CLAUDE.md") if (proj / name).is_file()]
    if not instr_files:
        errors.append("C10 neither AGENTS.md nor CLAUDE.md found at project root")
    else:
        rel_k = root.name
        for inf in instr_files:
            txt = inf.read_text(errors="replace")
            if rel_k not in txt and "@AGENTS.md" not in txt:
                errors.append(f"C10 {inf.name} does not reference {rel_k}/ or @AGENTS.md")

    return {
        "valid": len(errors) == 0,
        "resource_count": len(resources),
        "unreachable": unreachable,
        "errors": errors,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("knowledge_dir", type=Path)
    ap.add_argument("--project-root", type=Path, default=None)
    args = ap.parse_args()
    res = check_knowledge_dir(args.knowledge_dir, args.project_root)
    print(json.dumps(res, indent=2))
    return 0 if res["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
