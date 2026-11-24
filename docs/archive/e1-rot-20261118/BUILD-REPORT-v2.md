# E1 rot benchmark build report, v2

Revised 2026-11-18 in `~/oak-experiments/e1-rot-20261118/v2/`
against the coordinator review in `../REVISION-BRIEF.md`. The v1 files
stay untouched beside this directory. The pilot was not run, per the
brief. Everything up to and including the smoke test is done.

## What changed from v1, per review problem

| Review problem | Resolution |
|---|---|
| 1. No git in the guest | Custom Gondolin image with git and jq built and verified (below). All checks re-run with git/jq; truths re-verified in the snapshots. |
| 2. Tasks are lookups that name their source | Task set rewritten: every task is an action or decision task; no prompt names the file, ref, or command that holds the truth; no "right now", "currently", or "as the code ships"; scoring inspects deliverable files for the 4 action tasks. |
| 3. Task set biased against notes | New mix of 12: 6 stale-note, 4 note-needed, 2 controls, spread over the three repos. Every note-needed truth verified still true and absent from code, git, and kept files. |
| 4. check_ran too permissive | `check_ran` is now claim-specific (annotated check, equivalent command on the same source, or read of the specific record). The v1 behavior survives as `check_ran_loose`. |

## What exists in v2/

| Path | Content |
|---|---|
| `build-config.json`, `image-build.log`, `guest-image/` | the custom guest image build (337 MB) |
| `launch.py` | v1 launcher plus `GONDOLIN_GUEST_DIR` pointing at the image |
| `probe/` | v2 guest tool probe (`run-001/` evidence) |
| `tasks.json` | the 12 tasks with type, truth, stale values, strict and loose check patterns |
| `keys/` | one file per task: the verify command and its output |
| `conditions/` | 12 trees rebuilt from the snapshots; asis and nonotes are byte-identical to v1 (proven by `conditions-report.json`) |
| `annotate_conditions.py`, `annotation_diffcheck.py`, `diffcheck-result.json` | the 41-claim annotation table, applier, and diff proof |
| `evaluate.py`, `test_evaluate.py` | scorer (answer.json plus deliverable files) and its 52 unit tests |
| `make_trials.py`, `trials/` | 48 trial configs (12 tasks x 4 conditions) |
| `run_pilot.py` | seeded runner (seed 20261118, concurrency 2) with strict and loose check flags |
| `make_keys.py`, `build_conditions.py`, `conditions-report.json` | build scripts |
| `smoke/` | 4 smoke trials plus `results.jsonl` |

## Custom guest image (review problem 1)

Built with the gondolin CLI from
`~/oak-tools/node_modules/@earendil-works/gondolin`:

1. `node dist/bin/gondolin.js build --init-config` produced the default
   Alpine 3.23.7 x86_64 config.
2. `git` and `jq` were appended to `rootfsPackages` (`build-config.json`
   is the full config; the default package list is otherwise unchanged).
3. `node dist/bin/gondolin.js build --config v2/build-config.json
   --output v2/guest-image --tag e1-rot-git:latest`.

One failure on the first attempt: the host had no `lz4`, so the
initramfs step died with `sh: 1: lz4: not found`. The `lz4` package was
already installed but the binary was missing; after restoring it the
build completed (exit 0). Full log: `image-build.log`. Output
(337 MB in `guest-image/`): `vmlinuz-virt`, `initramfs.cpio.lz4`,
`rootfs.ext4`, krun assets, and `manifest.json` with sha256 checksums of
every asset and the exact package list.

The extension is unchanged from v1 (`~/oak-tools/pi-gondolin.ts`,
diff: none). `VM.create` resolves guest assets through the
`GONDOLIN_GUEST_DIR` override first, so `v2/launch.py` sets that variable
before exec'ing pi. It must be set inside launch.py because sudo scrubs
the caller environment. The image also carries the `e1-rot-git:latest`
tag in gondolin's local image store; the trial configs use the
`GONDOLIN_GUEST_DIR` path only.

### Guest probe re-run

One trivial trial through the real runner (`v2/probe/run-001/`, tiny git
repo as source, same pi arguments as every trial):

- Present and working: `git 2.52.1`, `jq`, `python3`, plus the v1 set
  (`grep`, `node`, `find`, `/bin/bash -lc`).
- `git log --oneline` and `git tag` work against the mounted workspace,
  including the snapshots' `.git` directories.
- `jq` processes JSON (probe computed `41 + 1 -> 42`).

Consequence: all check commands and truth verifications now use git and
jq where they are clearer (`git tag --sort=-v:refname`, `git grep`,
`git rev-parse`, `jq -r '.tasks[].status' ...`). The v1 fallbacks
(`ls .git/refs/tags/`, grep counting) are gone from the annotation table.

## Snapshots

Unchanged from v1 (`../snapshots/`, see the v1 report for the full
details and the drift warnings). All 12 v2 task truths were re-verified
inside these frozen snapshots with the new toolchain; `v2/keys/` holds
every command and its output. Note-needed truths that describe the host
machine were verified on the host (the commands are in the same key
files, marked `host`).

## The 12 tasks (review problems 2 and 3)

Mix: 6 stale-note, 4 note-needed, 2 controls. Spread: papercut 3,
looper 4, barista 5 (the protocol prefers 4/4/4; papercut could not
support a second strong stale-note or note-needed task, so looper and
barista carry one extra each). Every prompt is an ordinary user request
that ends with the fixed sentence and names its answer.json fields. No
prompt names the file, ref, or command holding the truth, and none uses
the banned cue words (checked mechanically).

| ID | Repo | Type | Defect (source) | Task shape | Truth | Stale / kept-file answer |
|---|---|---|---|---|---|---|
| p1-release-notes | papercut | stale | knowledge/index.md:20-23 (note file) | action: write the release notes file for the next patch release | next 0.2.4, `docs/releases/v0.2.4.md` | 0.2.2 (index lists only v0.2.0/v0.2.1 notes) |
| p2-measuretwice | papercut | note-needed | knowledge/index.md:20 (only record of authorization state) | decision: is the MeasureTwice experiment cleared to start? | false, proposed-no-authorization | true (kept opportunity doc reads as ready) |
| p3-close-control | papercut | control | docs/triage.md:56 (kept) | decision: how to close a report as fixed | `close` subcommand; no manual JSON edit | "no close command"; manual edit |
| l1-release-notes | looper | stale | NOTES.md:23+30 (note file) | action: draft release notes for the newest released version | 0.11.0 + `release-draft.md` | 0.10.0 (notes header) |
| l2-status-counts | looper | stale | NOTES.md:31 (note file) | action: draft STATUS.md weekly update with done/blocked/open counts | 125/7/7 | 113/9/1 |
| l3-operator-features | looper | stale | docs/OPERATOR-WORKFLOWS-PLAN.md:5 (note file) | decision: do the four operator features exist or must they be built? | exist (`publish --apply`, `requeue --fresh`, `config --set/--show`, `block_reason`) | "implementation proposal", must build |
| l4-t142 | looper | stale | .agent-memory/looper-t142-...md:11 (note file) | decision: can we build on T142's fix; backlog state? | code absent; cancelled | code present; done |
| b1-milestone-counts | barista | stale | LOG.md:115 (note file) | action: draft MILESTONE.md summary with todo/blocked/done counts | 2/28/93 | 10/26/88 |
| b2-android-setup | barista | note-needed | .agent-memory/android-toolchain-on-dev-box.md (only record of paths and approval) | decision/action: resume the Android port; where is the toolchain; is the preset approved? | `~/Android/Sdk`, `/usr/lib/jvm/java-21-openjdk-amd64`, approval still pending | "no toolchain / Java absent" (kept to-do.json T052 record) |
| b3-gdtoolkit | barista | note-needed | .agent-memory/looper-verify-home-redirect-...md (only true side of a three-way conflict) | decision: how are gdformat/gdlint set up here; quickest repair? | no pipx; pip user-site; fix shims | pipx install (kept README.md:24 and CLAUDE.md:16) |
| b4-grind-dial | barista | control | to-do.json T066 review note (kept) | decision: is grind_dial.tscn reachable in gameplay or deletable? | used; brew_stand_view.gd + tutorial_director.gd | unused; nothing instantiates it |
| b5-visual-check | barista | note-needed | .agent-memory/godot-visual-check-workflow.md (only record of this machine's render-check environment) | decision: how will exact render checks work; what to check before Xvfb? | PNG reads return a CDN URL; pixel sampler; check for running Xvfb first | none (no kept file teaches it; guesses score other) |

### Stale-note tasks

All six defects live in note files that nonotes removes
(`knowledge/`+`plans/`, `NOTES.md`+`.agent-memory/`+planning docs,
`LOG.md`+`.agent-memory/`). The truth is derivable from kept sources:
git tags and Cargo.toml (p1, l1), the backlog data (l2, l4), the CLI
source (l3). The smoke (l2) shows agents counting the data themselves
even in asis, which is the intended discrimination path: the note offers
a cheap wrong answer, the data is one command away.

### Note-needed tasks

Each note was verified still true on 2026-11-18, and each answer was
checked to be absent from code, git, and kept files:

- p2: `grep -rn authoriz` across the repo hits only the knowledge index
  line and PLAN.md's generic sentences; the opportunity doc (kept) never
  states an authorization.
- b2: no kept file mentions the SDK or JDK paths (grep empty);
  to-do.json T052 (kept) still records "Java as absent and Android
  deferred" — the kept file contradicts the note, which the brief calls
  a plus. Host checks confirm both paths and the export templates.
- b3: host checks confirm no pipx, the user-site gdtoolkit 4.5.0, and
  the hand-patched shims. README and CLAUDE.md (kept) teach pipx — a
  kept wrong file for nonotes agents to follow.
- b5: the CDN-URL read behavior, the pixel-sampler rule, and the
  long-lived Xvfb instances exist only in the memory (kept-file grep
  empty); `pgrep -a Xvfb` on the host confirms the Xvfb claim.

Expected direction: nonotes fails these. Wrong answers follow the kept
wrong file (stale) where one exists (p2, b2, b3) or are guesses (other;
b5 has no kept-file answer, so all its wrong answers are other).

### Controls

p3 and b4 keep their defects in files present in all four conditions
(docs/triage.md, to-do.json), byte-identical by construction. They
measure the model's ability to check code against a wrong kept document
without any note-file manipulation.

## Conditions and annotations

`v2/build_conditions.py` rebuilt all 12 trees from the snapshots with
the v1 notefiles.json lists (unchanged, hashed below). asis and nonotes
came out byte-identical to the v1 trees — `conditions-report.json`
records the comparison. oak and prose are asis plus annotations.

The annotation table (`v2/annotate_conditions.py`) keeps every v1 claim
anchor with claim text unchanged, upgrades checks to git/jq where
clearer, and adds three claims for the new tasks:

- papercut knowledge/index.md:20, the MeasureTwice authorization line
  (check: `git log --oneline -- docs/measuretwice-opportunity.md`).
- barista android memory, the "preset still needs Niko's approval" line.
- barista visual-check memory, the long-lived Xvfb line.

41 claims annotated, 82 insertions total:

| Repo | Claims | Files touched |
|---|---|---|
| papercut | 6 | index.md, journal, implementation-review.md |
| looper | 25 | NOTES.md, 3 plan docs, 9 memory files |
| barista | 10 | LOG.md (5 rows), 4 memory files |

Sample (looper NOTES.md:31) — claim text identical, check upgraded:

```
asis: - Backlog in `to-do.json`: 113 tasks done, 9 blocked, 1 todo.
oak:  - Backlog in `to-do.json`: 113 tasks done, 9 blocked, 1 todo. <!-- oak: { as_of: 2026-11-13, check: jq -r '.tasks[].status' to-do.json | sort | uniq -c } -->
prose:- Backlog in `to-do.json`: 113 tasks done, 9 blocked, 1 todo. *(As of 2026-11-13. Check with: jq -r '.tasks[].status' to-do.json | sort | uniq -c.)*
```

Sample (barista android memory, new) — a note-needed claim whose truth
cannot be checked inside the guest by design:

```
asis: preset still needs Niko's approval ([[android-on-device-pending]]).
oak:  preset still needs Niko's approval ([[android-on-device-pending]]). <!-- oak: { as_of: 2026-11-16, check: host: ls ~/Android/Sdk } -->
prose:preset still needs Niko's approval ([[android-on-device-pending]]). *(As of 2026-11-16. Check with: host: ls ~/Android/Sdk.)*
```

**Deviation, documented.** The protocol says a check "works inside the
guest". Note-needed claims describe the host machine, so no in-guest
check can exist — that is the definition of the task type. Their checks
carry a `host: ` prefix naming the command that verified the claim on
the host (the same commands saved in `v2/keys/`). Four claims carry such
checks (pipx, Android toolchain, Android approval, Xvfb). Running them
in the guest fails or returns not-found, which dates the claim without
being able to re-verify it — the same honest limitation the v1 report
recorded for its two skipped claims. The visual-check memory's
CDN-URL claim got no annotation at all (no command of any kind verifies
it); it is still scored in b5.

### Diffcheck

`v2/annotation_diffcheck.py` (the v1 script pointed at v2 trees):
**DIFFCHECK PASS** — 41 + 41 annotations stripped byte-exact, 0
mismatches, 0 extra or missing files, nonotes removals exact (papercut
4, looper 159, barista 28 files). Result in `v2/diffcheck-result.json`.

## Evaluator

`v2/evaluate.py TASK PROJECT` reads `{project}/answer.json` and, for the
four action tasks, the deliverable file:

- p1 requires `docs/releases/v0.2.4.md` to exist; l1 requires
  `release-draft.md`; l2 and b1 require STATUS.md / MILESTONE.md to
  contain the three true counts. A right answer without the deliverable
  scores `other` with a note, not `correct`.
- Note-needed tasks: correct = the note's truth; stale = the kept-file
  answer; other = a guess.
- v1's type coercion is kept (string integers, v-prefixed versions,
  case-insensitive enums, boolean strings).

`v2/test_evaluate.py`: **PASS**, 52 cases — correct/stale/other for all
12 tasks, deliverable present/missing/wrong-numbers for the 4 action
tasks, both b2 stale shapes, partial-evidence b4, coercion, bad json,
missing file, unknown task, non-object answer.

## Trials, runner, and check_ran (review problem 4)

48 configs in `v2/trials/` (source = `v2/conditions/<repo>-<cond>`,
agent through `v2/launch.py`, evaluator = `v2/evaluate.py`, 1200 s
timeout). `v2/run_pilot.py` seeds `random.Random(20261118).shuffle`,
runs at concurrency 2 through the unmodified skill runner, and writes
`results.jsonl` with both flags:

- `check_ran` (strict): true only if a bash command matched a
  task-specific `check_strict` regex (the annotated check or an
  equivalent on the same source — any `git tag` form for a tag claim,
  any counting pipeline over to-do.json for a tally claim, any grep for
  the load site for the scene claim), or the specific record was read
  through any tool (read-tool path or `cat`/`grep` of a
  `check_strict_reads` path, so reading via bash counts). Reading the
  note file that carries the claim, unrelated files, or unrelated parts
  of a file does not count: `to-do.json` reads alone no longer satisfy
  the tally claims; reading `grind_dial.tscn` does not satisfy b4;
  reading KNOWLEDGE.md or a memory file satisfies nothing.
- `check_ran_loose`: the v1 substring rule over all tool arguments,
  kept for comparison.

The strict matcher was validated against the v1 smoke logs (counting
pipelines in all four conditions detected; newline-spanning `python3 -c`
commands matched after a DOTALL fix). Note-needed tasks carry strict
patterns only for their contradiction records (for example T052 for b2)
and for host commands that cannot succeed in the guest, so their
`check_ran` is expected to be false in all conditions; that is the
honest reading of "no in-guest check exists".

## Smoke test

Four trials through `v2/run_pilot.py` (the real runner underneath): one
stale-note task (l2) and one note-needed task (p2), each in asis and
nonotes.

| Trial | Status | Label | Seconds | Tool calls | check_ran | check_ran_loose |
|---|---|---|---|---|---|---|
| l2 asis | valid | correct | 53.0 | 5 | true | true |
| l2 nonotes | valid | correct | 19.4 | 5 | true | true |
| p2 asis | valid | correct | 61.9 | 6 | true | true |
| p2 nonotes | valid | correct | 29.2 | 5 | true | true |

All four produced logs, prompt.txt, manifest.json, answer.json,
evaluation output, and results.jsonl. The l2 agents counted to-do.json
themselves (asis included — the stale NOTES.md tally did not bite in
this sample) and wrote real STATUS.md files. The p2 agents in both
conditions read the kept opportunity doc; the asis agent also read the
knowledge index, the nonotes agent reached "no authorization recorded"
by grepping kept files for authorization records and finding none.

## Doubts, compromises, and weak tasks

1. **p2 is the weakest task.** The smoke shows nonotes passing it by
   absence-of-evidence reasoning: no kept file records an
   authorization, and a careful agent concludes "not cleared". The
   prompt's enumerated status values also telegraph the answer shape.
   It stays because it is papercut's only note-needed candidate and the
   note is genuinely the only place the state is written down, but the
   pilot should expect a high nonotes correct rate on it.
2. **b5 has no stale label.** No kept file teaches the wrong answer, so
   every wrong b5 answer is `other`. The stale-action rate for b5 is
   structurally zero across conditions; only the correct rate
   discriminates.
3. **b2 paths are partially guessable.** `~/Android/Sdk` is
   the Android Studio default and a nonotes agent could guess it;
   scoring still requires the JDK path and the pending-approval state
   together, which are not guessable. A wrong-path answer scores
   `other`, which is the intended nonotes failure.
4. **l2 and b1 are still counts**, though no longer named-file lookups:
   the prompt asks for a deliverable document and never names
   to-do.json. The v1 smoke (prompt naming the file) showed a ceiling
   effect; whether removing the name restores discrimination is exactly
   what the pilot measures.
5. **l3 hangs on a plan-status defect** (proposal vs implemented). The
   agent-config-redesign proposal-status contradiction (NOTES.md:141)
   was considered and dropped as too similar a shape to l3; the audit's
   run-ref-tip defect (NOTES.md:22) was dropped as a pure lookup.
6. **Annotation scope is still targeted, not exhaustive** (v1
   compromise, unchanged): 41 claims of the hundreds in the note files.
7. **Host-check annotations for note-needed claims** are the protocol
   deviation recorded above; they date the claim but cannot re-verify
   it inside the guest.
8. **Task/repo imbalance**: papercut 3, looper 4, barista 5. Papercut's
   knowledge store could not support a second defensible stale-note or
   note-needed task after the release-history one; forcing 4/4/4 would
   have meant reusing one defect for two tasks.
9. **One model, one repetition planned**, matching the protocol; the
   pilot is descriptive only.
10. **The evaluator trusts answer.json plus exact deliverable paths.**
    An agent that writes correct content to a differently named file
    scores `other`, not `correct`. The prompts name the deliverable
    files explicitly, so this is judged fair.

## Freeze

Before the pilot, hash: the protocol
(`oak/docs/e1-rot-benchmark-protocol.md`,
`b186fd20a40e7a2e10e576f1ffc2cd2ff8e0f85afddffeed1d0c6218ddc32146`),
this report, `v2/tasks.json`
(`a30af54760dcfa2e664d9e186fab4e64e8f62b1ee1e33c53b107813123c5e9eb`),
`notefiles.json` (reused from v1 unchanged,
`48426b03e7c3b9431c2cac838be102dccc0374440980c74ec89e020ccd3d9f3c`),
`v2/evaluate.py`
(`1abde6dc6fb7f753e220c7625a6e3d5393d229a2df8209b07bec03b891aeba8b`),
`v2/run_pilot.py`
(`ccefa0cd71cef925139a072ad21a2e9fd679bede3ffbddd81486e044c523c71d`),
`v2/annotate_conditions.py`
(`8a6d9eaafb9c34790448724cbc877379951dcc19aa3dc1f4eafc8496da291772`),
`v2/build-config.json`
(`27e9edcf1739efec6b45cbc0014d0b694e61eadc833dafa1364bb0a21d992220`),
the 12 v2 condition trees (content hashes recorded at build time), and
the guest image (`guest-image/manifest.json` carries per-asset sha256).
The snapshots keep their v1 per-file manifests.
