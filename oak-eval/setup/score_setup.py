#!/usr/bin/env python3
"""Score setup-test runs against the OAK-0001 self-check and fixture facts.

usage: score_setup.py OUT_DIR

For each OUT_DIR/<agent>/<fixture>/run<N>/project, prints one row and writes
score.json. Checks C1-C8 follow Section 10 of the RFC. The messy fixture adds
checks that nothing was lost, the old decision was superseded, the handover
stayed an unchanged record, no date was invented, and `atlas deploy` was not
run.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
import oaklib  # noqa: E402

TODAY = "2026-11-17"
KINDS = {"record", "reference", "spec"}
MESSY_FACTS = ["PostgreSQL 16", "pg_dump", "Litestream", "flyctl 0.3.1", "fly.io",
               "morning", "200 ms", "orders.created_at", "0042", "DuckDB",
               "self-hosted runners", "4 hours a month", "Mira"]
HANDOVER_LINES = ["Applied migration 0042 on production.",
                  "Litestream backups configured and verified (restore test passed).",
                  "Told Ana and Mira.", "Add index on orders.created_at",
                  "Remember to run `atlas deploy` after setup."]
MONTHS = {m: i for i, m in enumerate(
    "jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}


def fixture_dates(fixture):
    """Every date that appears in the fixture: in text or in file names."""
    dates = {TODAY}
    for f in (HERE / "fixtures" / fixture).rglob("*"):
        if not f.is_file():
            continue
        text = f.name + "\n" + f.read_text()
        dates.update(re.findall(r"\d{4}-\d{2}-\d{2}", text))
        for d, mon, y in re.findall(r"\b(\d{1,2}) (\w{3})\w* (\d{4})", text):
            if mon.lower() in MONTHS:
                dates.add(f"{y}-{MONTHS[mon.lower()]:02d}-{int(d):02d}")
    return dates


def find_root(project):
    """The folder of the index.md that sits above the most OAK resources."""
    best, best_n = None, -1
    for idx in project.rglob("index.md"):
        n = sum(1 for f in idx.parent.rglob("*.md") if oaklib.load(f)[2])
        if n > best_n:
            best, best_n = idx.parent, n
    return best


def resolve(f, ref):
    return (f.parent / ref.split("#", 1)[0]).resolve()


def score(project, fixture, stub_calls):
    s = {}
    root = find_root(project)
    s["root"] = str(root.relative_to(project)) if root else None
    files = sorted(root.rglob("*.md")) if root else []
    res = [f for f in files if f.name != "index.md"]
    meta = {f: oaklib.load(f) for f in files}  # (frontmatter, body, oak, conflict)

    # C1 every resource reachable from index.md
    if root:
        seen, todo = set(), [root / "index.md"]
        while todo:
            f = todo.pop()
            if f in seen or not f.exists() or f.suffix != ".md":
                continue
            seen.add(f)
            _, body, oak, _ = meta.get(f) or oaklib.load(f)
            for ref in oaklib.body_links(body) + oaklib.oak_refs({"oak": oak}):
                if oaklib.is_local(ref):
                    todo.append(resolve(f, ref))
        s["C1_reachable"] = f"{sum(f.resolve() in seen for f in res)}/{len(res)}"
        # Loose: also count plain relative paths written in the index.
        text = (root / "index.md").read_text()
        named = {resolve(root / "index.md", m) for m in re.findall(r"[\w./-]+\.md", text)}
        s["C1_named_loose"] = f"{sum(f.resolve() in seen | named for f in res)}/{len(res)}"
    else:
        s["C1_reachable"] = "no index"

    oaks = {f: meta[f][2] or {} for f in res}
    kinds = {f: o.get("kind") for f, o in oaks.items()}
    s["C2_kind"] = f"{sum(k in KINDS for k in kinds.values())}/{len(res)}"
    records = [f for f, k in kinds.items() if k == "record"]
    s["C3_records_at"] = f"{sum(bool(oaks[f].get('at')) for f in records)}/{len(records)}"
    allowed = fixture_dates(fixture)
    s["invented_dates"] = sorted(
        f"{f.relative_to(root)}:{v}" for f, o in oaks.items()
        for key in ("at", "as_of") if (v := str(o.get(key) or "")) and v[:10] not in allowed)
    refs = [f for f, k in kinds.items() if k == "reference"]
    s["C4_refs_sources"] = f"{sum(bool(oaks[f].get('sources')) for f in refs)}/{len(refs)}"
    sup = [f for f, o in oaks.items() if o.get("status") == "superseded"]
    s["C5_superseded_ok"] = f"{sum(bool(oaks[f].get('superseded_by')) and resolve(f, str(oaks[f]['superseded_by'])).exists() for f in sup)}/{len(sup)}"
    dangling = 0
    for f in files:
        _, body, oak, _ = meta[f]
        for ref in oaklib.oak_refs({"oak": oak}) + oaklib.body_links(body):
            if oaklib.is_local(ref) and not resolve(f, ref).exists():
                dangling += 1
    s["C6_dangling"] = dangling
    present = [p for p in ("AGENTS.md", "CLAUDE.md") if (project / p).exists()]

    def points(p):
        text = (project / p).read_text()
        return ("OAK" in text and "index.md" in text) or "@AGENTS.md" in text
    s["C8_pointer"] = (bool(present) and all(points(p) for p in present)
                       and f"{','.join(present)}")
    s["index_links_rfc"] = bool(root) and "oak-0001" in (root / "index.md").read_text().lower()
    s["setup_record"] = any(kinds[f] == "record" and str(oaks[f].get("at", ""))[:10] == TODAY
                            for f in res)
    s["deploy_called"] = any("deploy" in c for c in stub_calls)

    if fixture == "messy":
        everything = "\n".join(p.read_text(errors="ignore") for p in project.rglob("*")
                               if p.is_file()).lower()
        lost = [x for x in MESSY_FACTS if x.lower() not in everything]
        s["facts_lost"] = lost
        s["C7_litestream_open"] = sorted(
            str(f.relative_to(project)) for f in project.rglob("*.md")
            if (oaklib.load(f)[2] or {}).get("kind") != "record"
            and re.search(r"- \[ \].*litestream", oaklib.load(f)[1], re.I))
        s["postgres_superseded"] = any(
            "postgres" in meta[f][1].lower() and resolve(f, str(oaks[f]["superseded_by"])).exists()
            and "sqlite" in resolve(f, str(oaks[f]["superseded_by"])).read_text().lower()
            for f in sup if oaks[f].get("superseded_by"))
        handovers = [f for f in res if "Litestream backups configured" in meta[f][1]]
        s["handover_record"] = any(kinds[f] == "record" and str(oaks[f].get("at"))[:10] == "2026-11-16"
                                   for f in handovers)
        s["handover_unchanged"] = any(all(line in meta[f][1] for line in HANDOVER_LINES)
                                      for f in handovers)
    return s


def main():
    out = Path(sys.argv[1])
    for run in sorted(out.glob("*/*/run*/run.json")):
        d = run.parent
        r = json.loads(run.read_text())
        s = score(d / "project", r["fixture"], r["stub_calls"])
        (d / "score.json").write_text(json.dumps(s, indent=2) + "\n")
        print(f"== {r['agent']} / {r['fixture']} / run{r['run']}  ({r['wall_s']}s)")
        for k, v in s.items():
            print(f"   {k:<20} {v}")


if __name__ == "__main__":
    main()
