"""Minimal helpers for reading and writing OAK Markdown frontmatter."""
import json
import re
from pathlib import Path

import yaml

FM_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.S)
MD_LINK_RE = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
REF_FIELDS = ("links", "sources", "superseded_by")
SIDECAR_SUFFIX = ".oak.json"


def split(text):
    """Return (frontmatter dict or None, body str)."""
    m = FM_RE.match(text)
    if not m:
        return None, text
    data = yaml.safe_load(m.group(1)) or {}
    return data, text[m.end():]


def join(meta, body):
    if not meta:
        return body
    fm = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{fm}\n---\n{body}"


def sidecar_path(path):
    path = Path(path)
    return path.with_name(path.name + SIDECAR_SUFFIX)


def load(path):
    """Return (frontmatter dict or None, body, oak dict or None, conflict).

    The oak block comes from the frontmatter or from `<file>.oak.json`.
    `conflict` is True when both are present (RFC §7.4).
    """
    path = Path(path)
    meta, body = split(path.read_text())
    oak = (meta or {}).get("oak")
    side = sidecar_path(path)
    conflict = False
    if side.exists():
        side_oak = (json.loads(side.read_text()) or {}).get("oak")
        conflict = oak is not None and side_oak is not None
        if oak is None:
            oak = side_oak
    return meta, body, oak, conflict


def oak_refs(meta):
    """All references in an oak block, as a flat list of strings."""
    oak = (meta or {}).get("oak") or {}
    out = []
    for field in REF_FIELDS:
        v = oak.get(field)
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, list):
            out.extend(x for x in v if isinstance(x, str))
    return out


CODE_RE = re.compile(r"^```.*?^```|^(?: {4}|\t).*?$|`[^`\n]*`", re.S | re.M)


def body_links(body):
    """Markdown link targets in the body, skipping code blocks and code spans."""
    return MD_LINK_RE.findall(CODE_RE.sub("", body))


def strip_links(body):
    """Body text with every Markdown link reduced to a placeholder."""
    return re.sub(r"\[[^\]]*\]\([^)]*\)", "[]()", body).strip()


def is_local(ref):
    return "://" not in ref and not ref.startswith(("mailto:", "#"))
