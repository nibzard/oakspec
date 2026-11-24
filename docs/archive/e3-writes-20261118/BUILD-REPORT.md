# E3 parallel-writes experiment build report

Built 2026-11-18 in `~/oak-experiments/e3-writes-20261118/`.
The pilot was not run, per the brief. Everything up to and including the
smoke test (3 complete rounds) is done.

Protocol: `oak/docs/e3-parallel-writes-protocol.md`
sha256 `5883f2c99886296aacea2324f9493b31f5f093f1f922a3a4ead5ce1479791a09`
(freeze this hash before the pilot).

## What exists here

| Path | Content |
|---|---|
| `scenarios.py` | pure spec: 4 scenarios, subjects, 9 records each, writer tasks, 6 reader questions each |
| `layouts.py` | renders the same records as shared / oak-index / append |
| `build_scenarios.py` | builds the 12 seed repos with backdated history; verifies them |
| `seeds/` | 12 seed repos (4 scenarios x 3 layouts), 7 commits each |
| `seeds-manifest.json` | verification report and seed unit-test results |
| `launch.py` | sudo/KVM launcher, reusing the E1 v2 git-enabled guest image read-only |
| `session.py` | one unattended Pi session in a guest over a work dir (run_trial.py semantics, in place) |
| `run_round.py` | one round: clone, 3 worktrees, 3 concurrent writers, fixed-order merges, resolver, reader |
| `score_round.py` | scorer: lost records, wrong current, stale overwrites, conflicts, resolver calls, reader accuracy |
| `test_score_round.py` | 9 unit tests on hand-made merges |
| `run_pilot.py` | 36 rounds, seed 20261118, one round at a time, resumable |
| `probe/` | one-session infrastructure probe evidence |
| `smoke/` | 3 complete smoke rounds + `results.jsonl` |
| `smoke-run.log` | full smoke console log |

## Scenarios

Four small projects, all runnable with the guest's python3 (no third-party
packages), each with unit tests:

| Scenario | Kind | Code (tracked files) |
|---|---|---|
| `clipfetch` | CLI tool | package `clipfetch/` (cli, fetcher, store), tests, README |
| `statuspage` | web service + config | `server.py` (http.server), `checker.py`, `config.json`, `backends.json`, tests |
| `marksweep` | data pipeline | `etl.py` (CSV to JSON summary), `input/sample.csv`, tests |
| `atlas-docs` | docs site | `build.py` static generator, `pages/*.md`, `pages/changelog/`, tests |

Each seed repo has 7 backdated commits (author = the approving person,
dated at noon on the record date):

```
c1 skeleton, c2 D1, c3 D3, c4 D4, c5 D2, c6 D5, c7 D6   (tip = main)
```

Writer C branches from c5 = HEAD~2, so its knowledge is stale by exactly
D5 and D6. Writer C's base was verified in every seed: the D5 and D6
marker phrases are absent at HEAD~2 and present at HEAD (build check).

Code constants move with the records (for example clipfetch
`TIMEOUT_SECONDS` is 10 at c4 and 30 at c6), so a stale checkout also has
stale code, and each writer's code change is in a file its own branch owns
or shares only loosely. A `.gitignore` keeps `__pycache__/` out of writer
commits.

## Records and replacement chains

Every scenario expresses the same shape with its own subjects. Six seeded
records with dates, approvers, and two seeded replacement chains, plus
three writer records dated 2026-11-18:

| Chain/record | Who | Replaces |
|---|---|---|
| D1 -> D2 | Maya | seeded chain 1 |
| D4 -> D5 | Priya | seeded chain 2 |
| D3 -> D9 | Luis | writer C's replacement (D3 is old, visible from the stale base) |
| D6 -> D8 | Priya | writer B's replacement (D6 is one of the records C never saw) |
| D7 | Luis | writer A's new subject, replaces nothing |

Subject example (clipfetch): retries D1/D2, output-format D3/D9, timeout
D4/D5, rate-limit D6/D8, progress-output D7. The other scenarios use the
same structure over their own subjects (port, cache-ttl, auth-header,
upstream-retries, health; date-format, dedup, chunk-size, output-name,
dry-run; toc-depth, changelog-policy, index-count, excerpt-length,
search). Every record carries a unique fixed-string `phrase` (scorer
marker) and a `value` (canonical short answer), and its body matches the
subject's extraction regex, in every version of the subject.

## Writer tasks

Per scenario, three tasks. Each prompt: read `KNOWLEDGE.md` first, make
one small code change, record one decision verbatim (ID, text, approver,
date, what it replaces). Prompts are identical across layouts and never
mention merging, other agents, or concurrency (checked by grep over all
smoke prompts). Writers get "You do not need git for this task; edit the
files directly" because git cannot work in a worktree mount (see doubts).

Example (writer C, clipfetch): change `store.py`/`cli.py` to save raw
HTML, record D9 "Clipped pages are saved as raw HTML (.html) without
Markdown conversion. This replaces D3.", approver Luis, 2026-11-18.

The maintenance guidance in `KNOWLEDGE.md` is byte-identical in all
layouts except the one sentence that names the layout (verified by the
build for all four scenarios):

- shared: all knowledge in `NOTES.md` ("Current state" + decision log)
- oak-index: `knowledge/` topic files listed by `knowledge/index.md`
- append: one dated file per record in `knowledge/records/`, never edited

## Layout samples

Seed tip for marksweep, same records in each layout:

`shared` NOTES.md:
```
## Current state
- Input date format: Input dates are parsed as YYYY-MM-DD (ISO 8601) (D2, 2026-10-19, Maya)
- Duplicate handling: For duplicate keys the first row wins; later rows are dropped (D3, 2026-10-09, Luis)
...
## Decision log
### D1 - Input date format (2026-10-06, approved by Maya)
Superseded by D2.
Input dates are parsed as %d/%m/%Y.
```

`oak-index` knowledge/index.md + knowledge/date-format.md:
```
---
oak:
  kind: reference
  status: current
  as_of: 2026-11-08
---
- [Input date format](date-format.md): Input dates are parsed as YYYY-MM-DD (ISO 8601) (D2, 2026-10-19, Maya)
```
```
---
oak:
  kind: record
  at: 2026-10-19
  approver: Maya
  status: current
---
# Input date format
Current decision: Input dates are parsed as YYYY-MM-DD (ISO 8601) (D2, 2026-10-19, Maya; replaces D1)
## Records
### D1 - Input date format (2026-10-06, approved by Maya) - superseded by D2
...
```

`append` knowledge/records/2026-10-19-d2-date-format.md:
```
# D2 - Input date format
- Date: 2026-10-19
- Approver: Maya
- Subject: date-format
- Replaces: D1

Input dates are parsed as YYYY-MM-DD (ISO 8601).
```

The oak-index format mirrors the E1 `papercut-oak` condition, which
followed OAK-0001 v0.3 Section 8.

## Orchestration (run_round.py)

1. Fresh round directory (never reused). `git clone` the seed into
   `repo/`; record `main_pre`.
2. `git worktree add` `wt-a`, `wt-b` from HEAD and `wt-c` from HEAD~2,
   on branches `writer-a/b/c`. Host git only, per the brief.
3. Run the three writer sessions concurrently, each a fresh guest
   mounting only its worktree (`ThreadPoolExecutor(3)`, 1500 s timeout).
4. Commit each worktree on the host (`git add -A`; a writer that changed
   nothing is recorded as `no_change` and still merges as a no-op).
5. Merge into main in the fixed order a, b, c with `git merge --no-edit`
   (writer-a is always a fast-forward). On conflict: list conflicted
   files, run a fresh resolver session in `repo/` with exactly the
   protocol prompt "Resolve the merge conflicts and keep all project
   knowledge." (900 s), then complete the merge on the host (unless the
   resolver committed itself; detected via `MERGE_HEAD`). Leftover
   conflict markers are counted.
6. Score the merged knowledge state, then run a fresh reader session in
   `repo/` (900 s). The reader prompt requires answers from the knowledge
   files only, forbids git, and asks for `answer.json` with `q1..q6`
   string values. The file is copied out to `evidence/`.
7. Score the reader, write `evidence/score.json` and `round-summary.json`.

Evidence per round: prompts, per-session `agent.stdout/stderr/result.json`
(exit, seconds, timed_out, tool_calls parsed from Pi events),
`refs.json` (all ref shas, merge records, resolver results),
`score-knowledge.json`, `answer.json`, `score.json`. Answer keys and
scorers live at the experiment root, outside every mount. Guest HTTP
stays blocked (the unchanged E1 extension with an empty allowlist).

## Scorer (score_round.py) and its tests

- Presence: `git grep -F <phrase>` per record over refs
  {main_pre, writer-a, writer-b, writer-c} and final main, restricted to
  the layout's knowledge paths.
- Branch truth: expected current per subject = newest record (date, then
  spec order) that any branch carries. Writer failures therefore shift
  the key, not the blame.
- Lost records: present on any source ref, absent on final main. Split
  into lost-current and lost-history (a replaced record whose text
  vanished).
- Current claim per subject, by layout: shared = last matching line of
  the "Current state" section; oak-index = last matching line of
  `knowledge/index.md`; append = value in the newest-dated record file
  for the subject (date from the file's `Date:` line, filename fallback).
  Wrong = claim differs from expected; missing = no claim found.
- Stale overwrite: wrong current where the claim equals an older
  version's value.
- Reader: value matching with digit word-boundaries (so "12" does not
  match "2") and casefolded substrings otherwise; labels correct / stale
  / other / no_answer; replaced-question keys are skipped when the
  replacing writer recorded nothing.
- Also reports: merge conflicts and conflicted files, resolver tool
  calls, unresolved markers, writer session health.

`test_score_round.py` (9 tests, all passing) builds hand-made git repos
with a toy spec: clean merge, stale-clobber merge (lost M2/T2-style
records, missing claim, stale overwrite), append no-loss, oak-index with
a dropped bullet, section-leak guard (decision-log lines must not count
as current claims), reader labels including key-follows-branches on
writer failure, numeric boundary matching, and merge/resolver metric
plumbing.

## Pilot runner (run_pilot.py)

36 round names (`scenario-layout-r1..3`) shuffled with
`random.Random(20261118)`, run strictly one at a time (each round already
runs three sessions at once), resumable (existing round dirs are
skipped), `--only` and `--collect-only` supported, `results.jsonl`
appended per round. Not run, per the brief.

## Smoke test

One complete round per layout for clipfetch, through `run_pilot.py`
(the real path). All three rounds status `complete`:

| Round | Writers (s) | Conflicts (files) | Resolver calls | Markers left | Lost records | Reader |
|---|---|---|---|---|---|---|
| clipfetch-shared-r1 | 17 / 13 / 20 | 2 (2, NOTES.md) | 7 + 6 | 0 | 0 | 6/6 correct |
| clipfetch-append-r1 | 15 / 23 / 57 | 0 | - | 0 | 0 | 6/6 correct |
| clipfetch-oak-index-r1 | 110 / 107 / 111 | 2 (2, knowledge) | 8 | 0 | 0 | 6/6 correct |

Structural signature matches the design: shared and oak-index conflicted
and needed resolvers; append merged three new record files with no
conflict. Resolvers kept every record (merge commits such as "Merge
branch 'writer-c': resolve NOTES.md conflicts, keep all decisions
(D1-D9)"). Merged "Current state" carried all five subjects with the
expected values. Round wall time 85-178 s. Infrastructure probe before
the smoke: one 8.4 s session through the full launch path.

## Doubts and weak points

1. **Writers cannot use git in their worktrees.** A worktree's `.git`
   is a host-absolute pointer file, dead inside the guest mount. The
   writer prompts say "You do not need git", which suppresses most
   flailing, but a writer that tries git anyway gets a confusing fatal
   error. This is equal across layouts but adds variance.
2. **The resolver prompt is the protocol's single sentence.** It says
   nothing about the guest or how to find conflicts. The resolver runs
   in `repo/` where guest git does work, so it can `git status`; in the
   smoke it resolved everything with 6-8 tool calls. Still, a resolver
   that does not think to grep for markers could stall; the orchestrator
   completes the merge regardless and counts leftover markers.
3. **Ceiling effect in the smoke.** One repetition per layout lost
   nothing and scored 6/6. GLM 5.3 resolvers were diligent. The pilot
   needs its 3 repetitions and all 4 scenarios before the decision rule
   means anything; a null result ("no layout loses records") is a live
   outcome per the protocol.
4. **"Wrong current" is claim-location based.** For shared it reads the
   "Current state" section, for oak-index the index bullets, for append
   the newest dated file. If a writer puts the current decision in an
   unusual place, the scorer may report missing_claim even though a
   careful reader could find it. The last-match rule also means a writer
   that appends a second bullet without removing the old one is scored by
   the newer line.
5. **Marker-phrase dependence.** Lost-record detection greps the exact
   instructed phrase. Writers are told to record the decision text
   verbatim; a paraphrasing writer would be scored as "not recorded"
   rather than lost, which deflates loss counts for that record but never
   inflates them. Reader keys follow the same branch-union rule, so a
   paraphrased record is excluded from the key rather than scored
   against.
6. **Replaced-question validity.** "What was X before the change?"
   presumes the replacement happened. If writer B recorded nothing, that
   question is skipped (excluded from the denominator). If B recorded but
   the merge lost the record, the question stays and the reader is
   expected to answer from surviving history; a reader that notices the
   loss and answers with the current value is scored other, not stale.
7. **Fixed merge order a, b, c.** Writer-a always fast-forwards, so only
   b and c can conflict. Order effects (merging the stale branch first)
   are not studied; the protocol fixes the order, so this is by design,
   but it concentrates the interesting merges in two of three steps.
8. **Two conflicts at most per round** (merges b and c). The
   per-layout conflict ceiling is 2; oak-index knowledge/ merges
   sometimes conflict in a topic file and the index at once, counted as
   files, not merges.
9. **Writer quality is uncontrolled.** Nothing verifies the code change
   is correct or the tests pass after the writers ran; only session exit
   codes, no_change flags, and record presence are recorded. A writer
   that edits the wrong file but records the decision still counts as a
   recorded decision.
10. **One model, low thinking, one seed set.** Matches the protocol's
    Runs section, but layout comparisons are within this agent profile.
11. **`main_pre` doubles as writer A/B's branch point**, so seeded-record
    loss can only come from the b/c merges. That is the designed loss
    path (stale branch plus concurrent edit), not an omission.
12. **The guest image is E1's.** It is read from
    `e1-rot-20261118/v2/guest-image/` via `GONDOLIN_GUEST_DIR` and never
    written; if E1 removes it, E3 rounds stop booting. Its checksums are
    in E1's `guest-image/manifest.json`.

## Freeze before the pilot

Hash and record: the protocol doc (above), this report, `scenarios.py`,
`layouts.py`, `score_round.py`, `run_round.py`, `session.py`,
`run_pilot.py`, and the 12 seed tips (listed in `seeds-manifest.json`).
The seed repos already carry their own history; clone integrity is
checked by `refs.json` (`seed_tip`) per round.
