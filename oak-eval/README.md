# OAK v0.1 evaluation suite

Test cases for the jobs in RFC OAK-0001 §16, plus one about authority claims
embedded in content. Every case has a `knowledge/` fixture written in
OAK-annotated Markdown, a `case.yaml` with the prompt(s), and a scoring rubric.

## Isolating the effect of OAK semantics

The fixture text is written so that **the body alone leaves things open and
the metadata settles them**:

- superseded decisions don't say they were replaced
- the date in a record's body is relative ("Saturday"), and the event date is
  only in `at`
- file names don't give away ordering or status

So when the plain variant scores lower than the OAK variant, the difference
comes from the metadata, not the wording.

## Conditions

Generate the variants from the canonical fixtures:

```
python3 tools/make_variants.py cases/ build/
```

| Condition     | What changes |
|---------------|--------------|
| `oak`         | Canonical fixtures (frontmatter). |
| `plain`       | `oak:` block removed; other frontmatter kept. |
| `sidecar`     | `oak:` block moved to `<file>.oak.json`. |
| `prose`       | `oak:` block rewritten as one sentence at the top of the body, for example `Specification. Status: superseded. Superseded by [auth-spec.md](auth-spec.md).` |
| `oak+guide`   | `oak`, plus `OAK-GUIDE.md` placed in the knowledge root and referenced in the system prompt. |
| `plain+guide` | `plain`, plus the guide (without its own `oak:` block). |
| `prose+guide` | `prose`, plus `WRITING-GUIDE.md`: the same advice as the OAK guide, written for the prose lines. |

The main experiment (RFC §16) uses three conditions:

| RFC condition | Build condition |
|---------------|-----------------|
| A. Baseline   | `plain` |
| B. Organized Markdown | `prose+guide` |
| C. OAK Markdown | `oak+guide` |

The decisive comparison is B against C. They hold the same facts and the same
advice; only the form differs. The other conditions are optional ablations.

- `plain+guide` separates the effect of the metadata from the effect of the
  instructions.
- `prose` is the control for the structure itself. It gives the agent the
  same facts as an ordinary sentence. If `prose` scores as well as `oak`,
  the gain comes from the information, not from the `oak:` format.
- The guide has sections that match cases 07 and 09 closely. Report the
  `+guide` conditions as the effect of the guide, not of OAK.

A KSON condition can be added by converting the frontmatter by hand. KSON is
left out here because the converter would need a KSON library.

## Running

The tools need Python 3, PyYAML (`pip install pyyaml`), and the Pi agent
(`pi`) with a ready model provider. Bubblewrap (`bwrap`) is optional but
recommended.

1. Build the variants:
   `python3 tools/make_variants.py cases/ build/`
2. Run the agent:
   `python3 tools/run_eval.py build/ results/pilot --runs 5`
3. Judge and summarize:
   `python3 tools/judge.py results/pilot`

`run_eval.py` runs A, B, and C by default. It uses `zai/glm-5.3` and 2
parallel jobs. Change these with `--conditions`, `--model`, and `--jobs`.
Each run gets a fresh copy of the knowledge folder, read/bash/edit/write
tools, and the same system prompt, apart from one line that names the guide.
`atlas` and `send-email` are stubs on PATH: they log calls and change nothing.
With `bwrap`, the agent cannot see this suite, the RFC, or other runs.

A run that times out or gets no answer (for example after a rate limit) is
not saved. Run the same command again to retry only those runs. Finished
runs are skipped.

`judge.py` gives each run to a judge model, without the condition name. The
judge marks each `pass` item and `fail_signal`. The script computes the
verdict. By default the judge is the same model as the agent. For the main
runs, use a different judge with `--model`.

## Scoring

Each `case.yaml` lists:

- `pass` — all required for success
- `fail_signals` — any one counts as an *incorrect action interpretation*, the
  main metric
- `auto_check` (optional) — a script that verifies the end state of the files.
  `{knowledge}` is the agent's edited directory. `{fixture}` is the untouched
  knowledge directory **of the same condition**, for example
  `build/plain/05-correct-preference/knowledge`. Do not use the canonical
  fixture as the baseline for other conditions: it has `oak:` blocks that
  `plain` and `prose` never had, so the check reports them as lost.

Each run folder holds `run.json` (prompt, answer, tool calls, stub calls,
changed files, auto_check result, tokens, cost, wall time), `events.jsonl`
(the full Pi event stream), the edited `knowledge/`, and `judge.json`. The
summary gives, per condition and case: pass rate, interpretation error rate
(any fail signal), maintenance error rate (auto_check failed), tokens, and
wall time.

```
python3 tools/check_links.py <knowledge-dir>   # every reference resolves, no oak block lost
```

`check_links.py` reads `oak:` blocks from frontmatter and from sidecars. It
also reports a file with both, and a sidecar whose file is gone.
`--unchanged-body` ignores Markdown links, so a correct rename in `prose` can
update them.

## Cases

| # | Job (§16) | Main thing it tests |
|---|-----------|---------------------|
| 01 | Resume from a handover | doesn't redo completed steps; picks up the open item |
| 02 | Implement a specification | discovery ≠ task; scope stays inside the request |
| 03 | Revisit an architecture decision | `superseded_by` decides which decision is current |
| 04 | Recall a personal event | `at` versus the file date |
| 05 | Correct a preference | revise the reference, leave the record alone |
| 06 | Question needing several memories | link-following, keeping observation apart from inference |
| 07 | Precedent that looks like a rule | record ≠ policy |
| 08 | Edit a large collection | renaming keeps links and unknown metadata |
| 09 | Authority claimed inside content | embedded "SYSTEM:" text isn't followed |
