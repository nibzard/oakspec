"""Build the oakspec.dev blog: an index page and one page per post.

Posts live in publish/posts/<slug>.html as HTML fragments with a small
header block. Chart placeholders such as {{chart:replication}} are replaced
with inline SVG built from the data below. Light mode only, like the spec
site. Palette validated with the dataviz validator on #fbfaf6.
"""

import html
import re
from pathlib import Path

POSTS = Path(__file__).resolve().parent / "posts"

BLUE = "#2a78d6"     # categorical slot 1
ORANGE = "#eb6834"   # categorical slot 2
GRAY = "#a9a69c"     # de-emphasized marks
INK = "#1c1c1c"
INK2 = "#55534d"
GRID = "#e4e0d5"
SANS = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'

CSS = """
figure.chart { margin: 2rem 0; }
figure.chart .plot { overflow-x: auto; }
figure.chart svg { width: 100%; min-width: 520px; height: auto; display: block; }
figure.chart figcaption { font-size: .85rem; color: #55534d; margin-top: .4rem; }
figure.chart details { font-size: .8rem; margin-top: .4rem; }
figure.chart table { border-collapse: collapse; margin-top: .4rem; }
figure.chart th, figure.chart td { text-align: left; padding: .15rem .8rem .15rem 0;
  border-bottom: 1px solid #e4e0d5; font-weight: normal; }
figure.chart th { color: #55534d; }
.quote { border-left: 3px solid #ddd8cc; margin: 1rem 0; padding: .1rem 0 .1rem 1rem; }
.quote p { margin: 0 0 .3rem; }
.quote .who { font-family: ui-monospace, Menlo, monospace; font-size: .78rem; color: #55534d; }
.posts { list-style: none; padding: 0; }
.posts li { margin-bottom: 1.4rem; }
.posts .meta { display: block; }
.table-wrap { overflow-x: auto; margin: 1.2rem 0; }
table.post-table { width: 100%; border-collapse: collapse; font-size: .86rem; line-height: 1.45; }
table.post-table th, table.post-table td { text-align: left; padding: .35rem .7rem .35rem 0;
  border-bottom: 1px solid #e4e0d5; vertical-align: top; }
table.post-table th { color: #55534d; font-weight: 600; border-bottom: 1px solid #cbc5b6; }
"""


def esc(text):
    return html.escape(str(text), quote=True)


def svg_text(x, y, text, size=12, fill=INK2, anchor="start", weight="normal"):
    return (f'<text x="{x}" y="{y}" font-family=\'{SANS}\' font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(text)}</text>')


def table(head, rows):
    out = ["<details><summary>Show the data as a table</summary><table><tr>"]
    out += [f"<th>{esc(h)}</th>" for h in head]
    out.append("</tr>")
    for row in rows:
        out.append("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>")
    out.append("</table></details>")
    return "".join(out)


# False verifications out of 30 trials, one value per batch.
REPLICATION = [
    ("Plain notes", [("E1b", 13), ("Replication", 14), ("Rules-only batch", 12)], False),
    ("Where field + one-line rule", [("E1b", 11), ("Replication", 11)], False),
    ("Plain notes + R4 to R6", [("Rules-only batch", 2)], True),
    ("Notes with where + R4 to R6", [("Candidate check", 0), ("Replication", 2),
                                  ("Rules-only batch", 1)], True),
]


def chart_replication():
    w, left, right, top, row_h = 576, 222, 40, 34, 40
    h = top + row_h * len(REPLICATION) + 34
    x = lambda v: left + (w - left - right) * v / 30
    parts = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="rep-t">',
             '<title id="rep-t">False verifications out of 30 trials, by condition and batch</title>']
    for tick in (0, 10, 20, 30):
        parts.append(f'<line x1="{x(tick)}" y1="{top - 12}" x2="{x(tick)}" '
                     f'y2="{h - 30}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(svg_text(x(tick), h - 14, tick, 11, INK2, "middle"))
    parts.append(svg_text(x(30), h - 1, "false verifications out of 30", 11, INK2, "end"))
    for i, (label, points, rules) in enumerate(REPLICATION):
        cy = top + i * row_h + row_h / 2 - 8
        color = BLUE if rules else GRAY
        parts.append(svg_text(0, cy + 4, label, 13, INK, weight="600" if rules else "normal"))
        values = [v for _, v in points]
        if len(values) > 1:
            parts.append(f'<line x1="{x(min(values))}" y1="{cy}" x2="{x(max(values))}" '
                         f'y2="{cy}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
        for batch, value in points:
            parts.append(f'<g><title>{esc(label)}, {esc(batch)}: {value} of 30</title>'
                         f'<circle cx="{x(value)}" cy="{cy}" r="12" fill="transparent"/>'
                         f'<circle cx="{x(value)}" cy="{cy}" r="5.5" fill="{color}" '
                         f'stroke="#fbfaf6" stroke-width="2"/></g>')
        span = f"{min(values)}" if min(values) == max(values) else f"{min(values)}–{max(values)}"
        parts.append(svg_text(x(max(values)) + 12, cy + 4, span, 12, INK))
    parts.append("</svg>")
    rows = [(label, batch, value) for label, points, _ in REPLICATION for batch, value in points]
    return ('<figure class="chart"><div class="plot">' + "".join(parts) + "</div>" +
            "<figcaption>Each dot is one batch of 30 trials: six questions, five runs each. "
            "Blue rows include rules R4 to R6. The gray where row also had a one-line "
            "scope rule. Fewer is better.</figcaption>" +
            table(["Condition", "Batch", "False verifications (of 30)"], rows) + "</figure>")


# Correct runs out of 5 in the same-batch replication.
TASKS = [
    ("Android SDK and JDK paths", "true", (5, 5, 5)),
    ("How gdtoolkit is installed", "true", (4, 5, 5)),
    ("zcode binary is missing", "true", (0, 0, 5)),
    ("Installed looper version", "stale", (2, 5, 5)),
    ("node and claude versions", "stale", (1, 1, 5)),
    ("Path to Godot", "stale", (0, 3, 3)),
]
CONDITIONS = ("Plain notes", "Where + 1 rule", "Where + R4 to R6")


def chart_waffle():
    w, left, top, row_h, sq, gap = 576, 200, 46, 30, 13, 3
    col_w = (w - left) / 3
    h = top + row_h * len(TASKS) + 44
    parts = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="waf-t">',
             '<title id="waf-t">Correct runs out of five, per question and condition</title>']
    for j, name in enumerate(CONDITIONS):
        parts.append(svg_text(left + j * col_w, top - 18, name, 12, INK, weight="600"))
    for i, (task, kind, scores) in enumerate(TASKS):
        y = top + i * row_h
        parts.append(svg_text(0, y + 11, task, 13, INK))
        parts.append(svg_text(0, y + 24, f"note is {kind}", 10.5, INK2))
        for j, correct in enumerate(scores):
            x0 = left + j * col_w
            cell = [f'<g><title>{esc(task)}, {esc(CONDITIONS[j])}: {correct} of 5 correct</title>',
                    f'<rect x="{x0 - 3}" y="{y - 3}" width="{5 * (sq + gap) + 34}" '
                    f'height="{sq + 6}" fill="transparent"/>']
            for k in range(5):
                fill = BLUE if k < correct else ORANGE
                cell.append(f'<rect x="{x0 + k * (sq + gap)}" y="{y}" width="{sq}" '
                            f'height="{sq}" rx="2" fill="{fill}"/>')
            cell.append(svg_text(x0 + 5 * (sq + gap) + 4, y + 11, f"{correct}/5", 11, INK2))
            cell.append("</g>")
            parts += cell
    ly = h - 16
    parts.append(f'<rect x="0" y="{ly - 10}" width="12" height="12" rx="2" fill="{BLUE}"/>')
    parts.append(svg_text(18, ly, "correct", 12, INK))
    parts.append(f'<rect x="90" y="{ly - 10}" width="12" height="12" rx="2" fill="{ORANGE}"/>')
    parts.append(svg_text(108, ly, "wrong: mostly a false verify", 12, INK))
    parts.append("</svg>")
    rows = [(t, k, *[f"{s}/5" for s in sc]) for t, k, sc in TASKS]
    return ('<figure class="chart"><div class="plot">' + "".join(parts) + "</div>" +
            "<figcaption>One batch, one seed. Each square is one agent run. "
            "Totals: 12, 19, and 28 of 30 correct.</figcaption>" +
            table(["Question", "Note"] + list(CONDITIONS), rows) + "</figure>")


AUDIT = [
    ("Stale current state", 15), ("Conflicting notes", 9), ("Broken references", 7),
    ("Done and open work mixed up", 4), ("Missing or wrong dates", 4),
    ("Replaced, with no pointer", 4), ("Instructions to agents inside notes", 2),
    ("Unknown origin", 1),
]


def chart_audit():
    w, left, right, top, row_h, bar_h = 576, 250, 30, 8, 26, 14
    h = top + row_h * len(AUDIT) + 30
    x = lambda v: left + (w - left - right) * v / 15
    parts = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="aud-t">',
             '<title id="aud-t">46 verified defects in real project memory, by kind</title>']
    for tick in (0, 5, 10, 15):
        parts.append(f'<line x1="{x(tick)}" y1="{top}" x2="{x(tick)}" y2="{h - 26}" '
                     f'stroke="{GRID}" stroke-width="1"/>')
        parts.append(svg_text(x(tick), h - 10, tick, 11, INK2, "middle"))
    for i, (label, value) in enumerate(AUDIT):
        y = top + i * row_h + (row_h - bar_h) / 2
        parts.append(svg_text(0, y + 11, label, 12.5, INK))
        bw = x(value) - left
        parts.append(f'<g><title>{esc(label)}: {value}</title>'
                     f'<rect x="{left}" y="{y - 5}" width="{w - left - right}" height="{bar_h + 10}" fill="transparent"/>'
                     f'<path d="M{left},{y} h{bw - 4} a4,4 0 0 1 4,4 v{bar_h - 8} a4,4 0 0 1 -4,4 h-{bw - 4} z" '
                     f'fill="{BLUE}"/></g>')
        if i == 0:
            parts.append(svg_text(x(value) + 6, y + 11, value, 12, INK, weight="600"))
    parts.append("</svg>")
    return ('<figure class="chart"><div class="plot">' + "".join(parts) + "</div>" +
            "<figcaption>Notes, agent memory, logs, and backlogs in papercut, looper, and "
            "barista, each defect checked against code, git, or a running process.</figcaption>" +
            table(["Kind of defect", "Count"], AUDIT) + "</figure>")


def chart_relay():
    w, h = 576, 196
    box_bg = "#f1eee5"
    parts = [
        f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="rel-t">',
        '<title id="rel-t">Four-agent cross-vendor relay across parallel Git branches</title>',
        '<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 1 L 8 5 L 0 9 z" fill="{INK2}"/></marker></defs>',
    ]

    def node(x, y, bw, bh, head, sub1, sub2, border=INK, sw=1.2, dash=""):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(
            f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="5" '
            f'fill="{box_bg}" stroke="{border}" stroke-width="{sw}"{da}/>'
        )
        parts.append(svg_text(x + 10, y + 19, head, 11.5, INK, weight="600"))
        parts.append(svg_text(x + 10, y + 35, sub1, 10.5, INK2))
        parts.append(svg_text(x + 10, y + 50, sub2, 10.5, INK2))

    # Stage 1 -> Stage 2a / 2b -> Host Merge + Fault -> Stage 3
    node(2, 66, 124, 62, "1. Claude Code", "Opus 5.5", "Setup + v1 code")
    node(150, 16, 136, 62, "2a. Codex", "GPT-6.2 Sol", "Revoke SHA-1 branch")
    node(150, 116, 136, 62, "2b. Pi", "GLM 5.4", "120s cap + HANDOFF")
    node(310, 56, 120, 82, "Host git merge", "OAK: 0 conflicts", "Plain: NOTES.md", border=ORANGE, sw=1.5, dash="4 3")
    parts.append(svg_text(320, 124, "+ 120s -> 300s edit", 10.5, ORANGE, weight="600"))
    node(454, 66, 120, 62, "3. Antigravity", "Gemini 4 Neon", "Cold release gate", border=BLUE, sw=1.6)

    # Connectors
    arrows = [
        (126, 90, 148, 48),
        (126, 104, 148, 146),
        (286, 48, 308, 86),
        (286, 146, 308, 108),
        (430, 97, 452, 97),
    ]
    for x1, y1, x2, y2 in arrows:
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK2}" '
            'stroke-width="1.3" marker-end="url(#arr)"/>'
        )
    parts.append("</svg>")
    return (
        '<figure class="chart"><div class="plot">' + "".join(parts) + "</div>"
        "<figcaption>Phase 2 relay on <code>pallets/itsdangerous</code>: four agent CLIs "
        "pass one repo across two parallel Git branches and an edited note.</figcaption></figure>"
    )


COORDINATION = [
    ("Parallel git merge conflicts (9 merges)", 0, 9, 9, "0/9", "9/9"),
    ("Silent number change missed outside Git", 0, 3, 3, "0/3", "3/3"),
    ("GLM 5.4 banned probes + false verifies", 0, 4, 15, "0/15", "4/15"),
]


def chart_coordination():
    w, left, right, top, row_h = 576, 236, 52, 28, 48
    h = top + row_h * len(COORDINATION) + 42
    span = w - left - right
    parts = [
        f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="coord-t">',
        '<title id="coord-t">Coordination and scope failures: OAK v0.5 versus Plain Markdown</title>',
    ]
    for pct, label in ((0, "0%"), (0.5, "50%"), (1.0, "100%")):
        xp = left + span * pct
        parts.append(f'<line x1="{xp}" y1="{top - 8}" x2="{xp}" y2="{h - 34}" stroke="{GRID}" stroke-width="1"/>')
        parts.append(svg_text(xp, h - 18, label, 11, INK2, "middle"))
    for i, (label, oak_v, plain_v, denom, oak_s, plain_s) in enumerate(COORDINATION):
        y = top + i * row_h
        parts.append(svg_text(0, y + 18, label, 12.2, INK))
        # OAK bar (top, blue)
        ow = max(3, span * (oak_v / denom))
        parts.append(f'<rect x="{left}" y="{y + 3}" width="{ow}" height="12" rx="2" fill="{BLUE}"/>')
        parts.append(svg_text(left + ow + 6, y + 13, f"OAK {oak_s}", 11, BLUE, weight="600"))
        # Plain bar (bottom, orange)
        pw = max(3, span * (plain_v / denom))
        parts.append(f'<rect x="{left}" y="{y + 20}" width="{pw}" height="12" rx="2" fill="{ORANGE}"/>')
        parts.append(svg_text(left + pw + 6, y + 30, plain_s, 11, INK))
    ly = h - 4
    parts.append(f'<rect x="0" y="{ly - 10}" width="11" height="11" rx="2" fill="{BLUE}"/>')
    parts.append(svg_text(16, ly, "OAK v0.5", 11.5, INK))
    parts.append(f'<rect x="92" y="{ly - 10}" width="11" height="11" rx="2" fill="{ORANGE}"/>')
    parts.append(svg_text(108, ly, "Plain / shared Markdown (fewer failures is better)", 11.5, INK))
    parts.append("</svg>")
    rows = [(lbl, oak_s, plain_s) for lbl, _, _, _, oak_s, plain_s in COORDINATION]
    return (
        '<figure class="chart"><div class="plot">' + "".join(parts) + "</div>"
        "<figcaption>Failure rates across the 2026-11-24 parallel-merge, non-Git handoff, "
        "and GLM 5.4 boundary tests.</figcaption>"
        + table(["Measure", "OAK v0.5", "Plain / shared Markdown"], rows)
        + "</figure>"
    )


CHARTS = {
    "replication": chart_replication,
    "waffle": chart_waffle,
    "audit": chart_audit,
    "relay": chart_relay,
    "coordination": chart_coordination,
}


def load_posts():
    """Read posts: a header of 'key: value' lines, a blank line, then HTML."""
    posts = []
    for path in sorted(POSTS.glob("*.html"), reverse=True):
        head, body = path.read_text().split("\n\n", 1)
        meta = dict(line.split(": ", 1) for line in head.splitlines())
        meta["slug"] = path.stem
        meta["body"] = re.sub(r"\{\{chart:(\w+)\}\}", lambda m: CHARTS[m.group(1)](), body)
        posts.append(meta)
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts


BLOG_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{title}</title>
<meta name="description" content="{description}">
<style>{css}</style>
</head>
<body>
<header>
<p class="meta"><a href="/">OAK-0001</a> · <a href="/blog/">Blog</a> · <a href="/evidence.txt">Evidence</a></p>
{header}
</header>
<main>
{body}
</main>
<hr>
<footer>Open Agent Knowledge. Spec: <a href="/oak-0001.txt">{url}/oak-0001.txt</a></footer>
</body>
</html>
"""


def build(site, base_css, url):
    css = base_css + CSS
    posts = load_posts()
    blog = site / "blog"
    blog.mkdir()
    items = "".join(
        f'<li><span class="meta">{esc(p["date"])}</span>'
        f'<a href="/blog/{p["slug"]}/">{esc(p["title"])}</a><br>{esc(p["description"])}</li>'
        for p in posts)
    (blog / "index.html").write_text(BLOG_PAGE.format(
        title="Blog · OAK-0001", description="Notes and results from the OAK project.",
        css=css, url=url, header="<h1>Blog</h1><p class=\"sub\">Notes and results from the OAK project.</p>",
        body=f'<ul class="posts">{items}</ul>'))
    for p in posts:
        out = blog / p["slug"]
        out.mkdir()
        header = (f'<p class="meta">{esc(p["date"])}</p><h1>{esc(p["title"])}</h1>'
                  f'<p class="sub">{esc(p["description"])}</p>')
        (out / "index.html").write_text(BLOG_PAGE.format(
            title=esc(p["title"]), description=esc(p["description"]), css=css, url=url,
            header=header, body=p["body"]))
    return posts
