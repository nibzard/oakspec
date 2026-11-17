#!/usr/bin/env python3
"""Build the oakspec.dev static site from the plain-text spec.

usage: build_site.py

Writes publish/site/: index.html (the spec as plain HTML), oak-0001.txt (the
raw text, for agents), and llms.txt (a pointer for agents).
"""
import html
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = HERE / "oak-0001.txt"
SITE = HERE / "site"
URL = "https://oakspec.dev"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OAK-0001: Open Agent Knowledge</title>
<meta name="description" content="A plain-text convention for memory that people and AI agents share.">
<link rel="alternate" type="text/plain" href="/oak-0001.txt">
<style>
  body {{ margin: 2rem auto; max-width: 82ch; padding: 0 1rem;
         font: 15px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
         color: #1a1a1a; background: #fdfdfb; }}
  pre {{ white-space: pre-wrap; font: inherit; }}
  a {{ color: #2a5d34; }}
  .top {{ border-bottom: 1px solid #ddd; padding-bottom: .5rem; margin-bottom: 1rem; }}
  @media (prefers-color-scheme: dark) {{
    body {{ color: #e6e6e6; background: #141414; }} a {{ color: #8fd19e; }}
    .top {{ border-color: #333; }} }}
</style>
</head>
<body>
<p class="top">Plain text for agents: <a href="/oak-0001.txt">{url}/oak-0001.txt</a></p>
<pre>{body}</pre>
</body>
</html>
"""

LLMS = """# OAK-0001: Open Agent Knowledge

> A plain-text convention for memory that people and AI agents share.

To set up OAK memory, read the spec and follow Section 8 (Set up):

- [OAK-0001 (plain text)]({url}/oak-0001.txt)
"""


def main():
    text = SPEC.read_text()
    body = html.escape(text)
    body = re.sub(r"(https://[^\s<)]+)", r'<a href="\1">\1</a>', body)
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    (SITE / "index.html").write_text(PAGE.format(url=URL, body=body))
    shutil.copy2(SPEC, SITE / "oak-0001.txt")
    (SITE / "llms.txt").write_text(LLMS.format(url=URL))
    print(f"wrote {SITE}")


if __name__ == "__main__":
    main()
