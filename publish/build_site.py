#!/usr/bin/env python3
"""Build the oakspec.dev static site from the plain-text spec.

usage: build_site.py

Writes publish/site/: index.html (the spec as reflowable HTML), oak-0001.txt
(the raw text, for agents), evidence.txt, the archived oak-0001-v0.4.txt and
oak-0001-v0.3.txt, and llms.txt (a pointer for agents).

The text uses a small set of plain-text conventions. This script turns them
into HTML so the page reflows on small screens:

  NO INDENT          a section heading
  indent >= 6        a code block (when it starts a block)
  "- " item          a bullet list
  "1. " item         a numbered list ("a. " items nest inside)
  term  definition   a definition list (term, then two or more spaces)
  anything else      a paragraph; its lines are joined
"""
import html
import re
import shutil
from pathlib import Path

import blog

HERE = Path(__file__).resolve().parent
SPEC = HERE / "oak-0001.txt"
SITE = HERE / "site"
URL = "https://oakspec.dev"

SUBHEAD_RE = re.compile(r"^  \d+\.\d+\s+\S")
NESTED_RE = re.compile(r"^ {8}(\S+)\s{2,}(\S.*)$")
TERM_RE = re.compile(r"^  (\S(?:.{0,22}?\S)?)\s{2,}(\S.*)$")
STEP_RE = re.compile(r"^\s{2,4}(\d+)\.\s+(.*)$")
SUBSTEP_RE = re.compile(r"^\s{5,}([a-z])\.\s+(.*)$")

BASE_CSS = """html { background: #fbfaf6; }
body { max-width: 36rem; margin: 0 auto; padding: 3rem 1.25rem 5rem;
  font: 17px/1.6 "Iowan Old Style", "Palatino Linotype", Palatino, Georgia,
  "Times New Roman", serif; color: #1c1c1c; }
header { margin-bottom: 2.5rem; }
.meta, dt, code, pre, footer { font-family: ui-monospace, "SF Mono", Menlo,
  Consolas, "Courier New", monospace; }
.meta { font-size: .8rem; letter-spacing: .02em; color: #555; margin: 0; }
h1 { font-size: 1.9rem; font-weight: normal; line-height: 1.2;
  margin: .6rem 0 .4rem; }
.sub { font-style: italic; margin: 0 0 1rem; }
h2 { font-size: 1.1rem; margin: 2.6rem 0 .5rem; }
h3 { font-size: 1rem; margin: 1.8rem 0 .4rem; }
dd dl { margin: .4rem 0 .4rem; }
dd p { margin: .4rem 0 0; }
p, ul, ol, dl { margin: 0 0 1rem; }
ul, ol { padding-left: 1.4rem; }
li { margin-bottom: .35rem; }
li > p, li > pre { margin-top: .5rem; }
dt { font-size: .88rem; font-weight: 600; margin-top: .8rem; }
dd { margin: .1rem 0 0 1.4rem; }
pre { font-size: .8rem; line-height: 1.45; background: #f1eee5;
  padding: .8rem 1rem; overflow-x: auto; margin: 0 0 1rem; }
a { color: #1a0dab; }
a:visited { color: #551a8b; }
hr { border: 0; border-top: 1px solid #ddd8cc; margin: 3rem 0 1rem; }
footer { font-size: .8rem; color: #555; }
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>OAK-0001: Open Agent Knowledge</title>
<meta name="description" content="{subtitle}.">
<link rel="alternate" type="text/plain" href="/oak-0001.txt">
<style>
html {{ background: #fbfaf6; }}
body {{ max-width: 36rem; margin: 0 auto; padding: 3rem 1.25rem 5rem;
  font: 17px/1.6 "Iowan Old Style", "Palatino Linotype", Palatino, Georgia,
  "Times New Roman", serif; color: #1c1c1c; }}
header {{ margin-bottom: 2.5rem; }}
.meta, dt, code, pre, footer {{ font-family: ui-monospace, "SF Mono", Menlo,
  Consolas, "Courier New", monospace; }}
.meta {{ font-size: .8rem; letter-spacing: .02em; color: #555; margin: 0; }}
h1 {{ font-size: 1.9rem; font-weight: normal; line-height: 1.2;
  margin: .6rem 0 .4rem; }}
.sub {{ font-style: italic; margin: 0 0 1rem; }}
h2 {{ font-size: 1.1rem; margin: 2.6rem 0 .5rem; }}
h3 {{ font-size: 1rem; margin: 1.8rem 0 .4rem; }}
dd dl {{ margin: .4rem 0 .4rem; }}
dd p {{ margin: .4rem 0 0; }}
p, ul, ol, dl {{ margin: 0 0 1rem; }}
ul, ol {{ padding-left: 1.4rem; }}
li {{ margin-bottom: .35rem; }}
li > p, li > pre {{ margin-top: .5rem; }}
dt {{ font-size: .88rem; font-weight: 600; margin-top: .8rem; }}
dd {{ margin: .1rem 0 0 1.4rem; }}
pre {{ font-size: .8rem; line-height: 1.45; background: #f1eee5;
  padding: .8rem 1rem; overflow-x: auto; margin: 0 0 1rem; }}
a {{ color: #1a0dab; }}
a:visited {{ color: #551a8b; }}
hr {{ border: 0; border-top: 1px solid #ddd8cc; margin: 3rem 0 1rem; }}
footer {{ font-size: .8rem; color: #555; }}
</style>
</head>
<body>
<header>
<p class="meta">{meta}</p>
<h1>{title}</h1>
<p class="sub">{subtitle}</p>
<p class="meta">Plain text for agents: <a href="/oak-0001.txt">{url}/oak-0001.txt</a></p>
</header>
<main>
{body}
</main>
<hr>
<footer>End of OAK-0001. <a href="/oak-0001.txt">Plain text</a> · <a href="/evidence.txt">Evidence</a> · <a href="/blog/">Blog</a>.</footer>
</body>
</html>
"""

LLMS = """# OAK-0001: Open Agent Knowledge

> A plain-text convention for memory that people and AI agents share.

To set up OAK memory, read the spec and follow Section 8 (Set up):

- [OAK-0001 (plain text)]({url}/oak-0001.txt)
- [Evidence behind the spec]({url}/evidence.txt)
- [Previous version, v0.4]({url}/oak-0001-v0.4.txt)
- [Previous version, v0.3]({url}/oak-0001-v0.3.txt)
- [Blog]({url}/blog/)
"""


def inline(text):
    text = html.escape(text, quote=False)
    return re.sub(r"(https://[^\s<)]+?)([.,;]?)(?=\s|$|\))", r'<a href="\1">\1</a>\2', text)


def join(lines):
    return " ".join(line.strip() for line in lines)


def indent(line):
    return len(line) - len(line.lstrip(" "))


def heading(line):
    text = line.strip()
    m = re.match(r"(\d+\.\s+)?(.*)", text)
    words = m.group(2).capitalize()
    return f"<h2>{html.escape((m.group(1) or '') + words)}</h2>"


def blocks(lines):
    out, cur = [], []
    for line in lines:
        if line.strip():
            cur.append(line.rstrip())
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def split_items(block, starts):
    """Split a block into items: a new item starts where starts(line) is true."""
    items = []
    for line in block:
        if starts(line) or not items:
            items.append([line])
        else:
            items[-1].append(line)
    return items


def definition(lines):
    """Render a definition; deeper indented "term  text" lines form a nested list."""
    lead, nested, tail = [], [], []
    for line in lines:
        m = NESTED_RE.match(line)
        if m and not tail:
            nested.append(list(m.groups()))
        elif nested and indent(line) >= 8:
            nested[-1][1] += " " + line.strip()
        elif nested:
            tail.append(line)
        else:
            lead.append(line)
    out = inline(join(lead))
    if nested:
        out += "<dl>" + "".join(f"<dt>{html.escape(t)}</dt><dd>{inline(d)}</dd>"
                                for t, d in nested) + "</dl>"
    if tail:
        out += f"<p>{inline(join(tail))}</p>"
    return out


def render_section(lines):
    html_out = []
    open_list = None  # "ol", "ul", or "dl" while consecutive blocks continue it

    def close():
        nonlocal open_list
        if open_list:
            html_out.append(f"</li></{open_list}>" if open_list != "dl" else "</dl>")
            open_list = None

    for block in blocks(lines):
        first = block[0]
        if indent(first) >= 6:
            code = "\n".join(line[indent(first):] if line[:indent(first)].isspace()
                             else line.strip() for line in block)
            html_out.append(f"<pre>{html.escape(code)}</pre>")
            continue  # a code block may sit inside an open list item
        if STEP_RE.match(first):
            if open_list != "ol":
                close()
                html_out.append("<ol>")
                open_list = "ol"
            else:
                html_out.append("</li>")
            sub_open = False
            for i, item in enumerate(split_items(block, lambda l: bool(STEP_RE.match(l)
                                                                     or SUBSTEP_RE.match(l)))):
                m = SUBSTEP_RE.match(item[0])
                if m:
                    if not sub_open:
                        html_out.append('<ol type="a">')
                        sub_open = True
                    html_out.append(f"<li>{inline(join([m.group(2)] + item[1:]))}</li>")
                    continue
                if sub_open:
                    html_out.append("</ol>")
                    sub_open = False
                if i > 0:
                    html_out.append("</li>")
                html_out.append(f"<li>{inline(join([STEP_RE.match(item[0]).group(2)] + item[1:]))}")
            if sub_open:
                html_out.append("</ol>")
            continue
        if open_list == "ol" and indent(first) >= 3:
            html_out.append(f"<p>{inline(join(block))}</p>")  # more text in the step
            continue
        if first.lstrip().startswith("- "):
            close()
            items = split_items(block, lambda l: l.lstrip().startswith("- "))
            html_out.append("<ul>" + "".join(
                f"<li>{inline(join([it[0].lstrip()[2:]] + it[1:]))}</li>" for it in items) + "</ul>")
            continue
        if TERM_RE.match(first) and indent(first) == 2:
            if open_list != "dl":
                close()
                html_out.append("<dl>")
                open_list = "dl"
            for item in split_items(block, lambda l: indent(l) == 2 and bool(TERM_RE.match(l))):
                term, rest = TERM_RE.match(item[0]).groups()
                html_out.append(f"<dt>{html.escape(term)}</dt><dd>{definition([rest] + item[1:])}</dd>")
            continue
        if len(block) == 1 and SUBHEAD_RE.match(first):
            close()
            html_out.append(f"<h3>{html.escape(first.strip())}</h3>")
            continue
        close()
        html_out.append(f"<p>{inline(join(block))}</p>")
    close()
    return "\n".join(html_out)


def render(text):
    lines = text.splitlines()
    head = [re.split(r"\s{2,}", l.strip()) for l in lines[:3]]
    title, status = head[0]
    subtitle, version = head[1]
    _, date = head[2]
    rest = lines[3:]
    sections, cur_head, cur = [], None, []
    for line in rest:
        if line.strip() and indent(line) == 0:
            if cur_head is not None or any(l.strip() for l in cur):
                sections.append((cur_head, cur))
            cur_head, cur = line, []
        else:
            cur.append(line)
    sections.append((cur_head, cur))
    body = []
    for head_line, sec in sections:
        if head_line is None:
            continue
        if head_line.startswith("END OF"):
            continue
        body.append(heading(head_line))
        body.append(render_section(sec))
    number, name = title.split(": ", 1)
    meta = f"{number} &middot; {status} &middot; {version} &middot; {date}"
    return PAGE.format(meta=meta, title=html.escape(name), subtitle=html.escape(subtitle),
                       url=URL, body="\n".join(body))


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    (SITE / "index.html").write_text(render(SPEC.read_text()))
    shutil.copy2(SPEC, SITE / "oak-0001.txt")
    for extra in ("oak-0001-v0.4.txt", "oak-0001-v0.3.txt", "evidence.txt"):
        shutil.copy2(HERE / extra, SITE / extra)
    (SITE / "llms.txt").write_text(LLMS.format(url=URL))
    blog.build(SITE, BASE_CSS, URL)
    print(f"wrote {SITE}")


if __name__ == "__main__":
    main()
