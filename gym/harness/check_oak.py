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
import datetime
import json
from pathlib import Path
import re
import subprocess
import sys
import yaml

FM_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.S)
CODE_RE = re.compile(r"^```.*?^```|^(?: {4}|\t).*?$|`[^`\n]*`", re.S | re.M)
MD_LINK_RE = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}.*)?$")

VALID_KINDS = {"record", "reference", "spec"}
VALID_ORIGINS = {"user", "agent", "inferred", "external"}
REF_FIELDS = ("links", "sources", "superseded_by")
OAK_KNOWN_KEYS = {"kind", "status", "at", "as_of", "origin", "sources", "links", "superseded_by", "where"}
OAK_ONLY_KEYS = {"as_of", "superseded_by"}
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


def git_last_modified_iso(proj_root: Path, target: Path) -> str | None:
    if not (proj_root / ".git").exists():
        return None
    try:
        rel = target.resolve().relative_to(proj_root.resolve())
    except ValueError:
        return None
    proc = subprocess.run(
        ["git", "-C", str(proj_root), "log", "-1", "--format=%cs", "--", str(rel)],
        capture_output=True,
        text=True,
        check=False,
    )
    val = proc.stdout.strip()
    return val if proc.returncode == 0 and len(val) >= 10 else None


def check_knowledge_dir(knowledge_dir: Path, project_root: Path | None = None) -> dict:
    root = knowledge_dir.resolve()
    proj = (project_root or root.parent).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not root.is_dir():
        return {"valid": False, "errors": [f"knowledge folder not found: {root}"], "resource_count": 0}

    md_files = sorted(root.rglob("*.md"))
    resources = [f for f in md_files if f.name != "index.md"]
    loaded = {f: load_resource(f) for f in md_files}

    for f in md_files:
        rel = f.relative_to(root)
        meta, body, oak, conflict = loaded[f]
        if conflict:
            errors.append(f"{rel}: has both frontmatter oak block and {SIDECAR_SUFFIX} sidecar")
        if isinstance(meta, dict):
            check_keys = OAK_KNOWN_KEYS if oak is not None else OAK_ONLY_KEYS
            misplaced = sorted(k for k in meta.keys() if k != "oak" and k in check_keys)
            if misplaced:
                errors.append(f"{rel}: OAK field(s) {misplaced} at top-level frontmatter instead of nested under 'oak:'")
        if oak is not None:
            if not isinstance(oak, dict):
                errors.append(f"{rel}: oak metadata must be a mapping")
                continue
            kind = oak.get("kind")
            if not isinstance(kind, str) or kind not in VALID_KINDS:
                errors.append(f"{rel}: C1 invalid or missing kind {kind!r}")
            origin = oak.get("origin")
            if origin is not None and (not isinstance(origin, str) or origin not in VALID_ORIGINS):
                errors.append(f"{rel}: invalid origin {origin!r} (must be one of {sorted(VALID_ORIGINS)} or omitted)")
            at_val = oak.get("at")
            as_of_val = oak.get("as_of")
            if at_val is not None:
                if kind != "record":
                    errors.append(f"{rel}: C2 'at' is only for records (found on {kind!r})")
                elif not isinstance(at_val, (str, datetime.date, datetime.datetime)) or not ISO_DATE_RE.match(str(at_val)):
                    errors.append(f"{rel}: C2 'at' is not ISO 8601 date: {at_val!r}")
            if as_of_val is not None:
                if kind == "record":
                    errors.append(f"{rel}: C3 'as_of' is not allowed on records")
                elif not isinstance(as_of_val, (str, datetime.date, datetime.datetime)) or not ISO_DATE_RE.match(str(as_of_val)):
                    errors.append(f"{rel}: C3 'as_of' is not ISO 8601 date: {as_of_val!r}")
                else:
                    as_of_day = str(as_of_val)[:10]
                    checked_targets: set[Path] = set()
                    for ref in oak_refs(oak) + body_links(body):
                        if not is_local(ref):
                            continue
                        tgt = resolve_ref(f, ref)
                        if not tgt.exists() or tgt in checked_targets or root in tgt.parents or tgt == root:
                            continue
                        checked_targets.add(tgt)
                        git_day = git_last_modified_iso(proj, tgt)
                        if git_day and git_day > as_of_day:
                            warnings.append(
                                f"{rel}: stale as_of ({as_of_day}) — linked path {ref!r} changed in git on {git_day}"
                            )
            status_val = oak.get("status")
            if status_val is not None and not isinstance(status_val, str):
                errors.append(f"{rel}: invalid status {status_val!r} (must be a string)")
            elif status_val == "superseded":
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
        "warnings": warnings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("knowledge_dir", type=Path)
    ap.add_argument("--project-root", type=Path, default=None)
    ap.add_argument(
        "--strict-stale",
        action="store_true",
        help="Exit non-zero if any linked repository path changed in git after as_of",
    )
    args = ap.parse_args()
    res = check_knowledge_dir(args.knowledge_dir, args.project_root)
    print(json.dumps(res, indent=2))
    if not res["valid"]:
        return 1
    if args.strict_stale and res["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
