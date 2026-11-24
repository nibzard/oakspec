"""Lightweight YAML frontmatter splitter for OAK experiment checks."""
import re
import yaml

FM_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.S)


def split_fm(text: str):
    m = FM_RE.match(text)
    if not m:
        return None, text
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except Exception:
        data = {}
    return data, text[m.end():]
