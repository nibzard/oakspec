# E1b check scope results

Date: 2026-11-19. 156 trials in `~/oak-experiments/e1b-scope-20261118/`:
120 E1b (6 tasks x 4 conditions x 5 repetitions) and 36 Flash (6 E1 stale-note
tasks x asis/nonotes x 3 repetitions). Seed 20261118, one seeded shuffle over
all 156, concurrency 2 (E3 rounds shared the machine). Model: GLM 5.3 at low
thinking for E1b, GLM 5.3 Flash at low thinking for the Flash group (model id
confirmed by probe, `probe/flash-model-probe.txt`). Every trial exited
normally: no timeouts, no agent failures, no missing trials. Data:
`runs/results.jsonl` (E1b), `flash/runs/results.jsonl` (Flash).
Protocol: `~/oak/docs/e1b-check-scope-protocol.md` (hashed in
`FREEZE-SHA256.txt` before the runs).

## The six tasks

| Task | Repo | Type | Note value (date) | Host today (keys/) |
|---|---|---|---|---|
| eb1-android | barista | true | SDK `~/Android/Sdk`, JDK `/usr/lib/jvm/java-21-openjdk-amd64`, preset unapproved (2026-11-16) | same |
| eb2-gdtools | barista | true | no pipx, `pip-user-site` (2026-11-18) | same |
| eb4-zcode | looper | true | zcode binary missing (2026-10-14) | missing |
| eb5-looperbin | looper | stale | installed binary 0.10.0 (2026-11-13) | 0.11.0 |
| eb6-nodeclaude | barista | stale | node v26.11.1, claude 2.1.284 (2026-10-13) | v24.18.0, 2.1.280 |
| eb7-godotpath | barista | stale | Godot at `/Applications/Godot.app` (2026-10-13) | `~/.local/bin/godot`; noted path absent |

No fact can be checked in the guest (verified per task in `keys/`). The
protocol's correct answer is therefore always the note value with status
`unverified` and the note's date on stale tasks; `contradicted` is not
correct for any E1b task because none has contrary evidence inside the
repository.

## E1b: per-task, per-condition label counts

| Task (type) | Condition | correct | false-reject | false-verify | invented | other |
|---|---|---|---|---|---|---|
| eb1-android (true) | asis | 4 | 1 | 0 | 0 | 0 |
| eb1-android (true) | unscoped | 5 | 0 | 0 | 0 | 0 |
| eb1-android (true) | scoped | 5 | 0 | 0 | 0 | 0 |
| eb1-android (true) | scoped-prose | 5 | 0 | 0 | 0 | 0 |
| eb2-gdtools (true) | asis | 4 | 1 | 0 | 0 | 0 |
| eb2-gdtools (true) | unscoped | 5 | 0 | 0 | 0 | 0 |
| eb2-gdtools (true) | scoped | 5 | 0 | 0 | 0 | 0 |
| eb2-gdtools (true) | scoped-prose | 5 | 0 | 0 | 0 | 0 |
| eb4-zcode (true) | asis | 0 | 0 | 5 | 0 | 0 |
| eb4-zcode (true) | unscoped | 0 | 0 | 5 | 0 | 0 |
| eb4-zcode (true) | scoped | 0 | 0 | 5 | 0 | 0 |
| eb4-zcode (true) | scoped-prose | 0 | 0 | 5 | 0 | 0 |
| eb5-looperbin (stale) | asis | 2 | 0 | 0 | 3 | 0 |
| eb5-looperbin (stale) | unscoped | 5 | 0 | 0 | 0 | 0 |
| eb5-looperbin (stale) | scoped | 4 | 0 | 0 | 1 | 0 |
| eb5-looperbin (stale) | scoped-prose | 5 | 0 | 0 | 0 | 0 |
| eb6-nodeclaude (stale) | asis | 0 | 0 | 5 | 0 | 0 |
| eb6-nodeclaude (stale) | unscoped | 0 | 0 | 5 | 0 | 0 |
| eb6-nodeclaude (stale) | scoped | 2 | 0 | 3 | 0 | 0 |
| eb6-nodeclaude (stale) | scoped-prose | 0 | 0 | 5 | 0 | 0 |
| eb7-godotpath (stale) | asis | 2 | 0 | 3 | 0 | 0 |
| eb7-godotpath (stale) | unscoped | 1 | 0 | 4 | 0 | 0 |
| eb7-godotpath (stale) | scoped | 2 | 0 | 3 | 0 | 0 |
| eb7-godotpath (stale) | scoped-prose | 4 | 0 | 1 | 0 | 0 |

## E1b: per-condition totals

| Condition | correct | false-reject | false-verify | invented | other | check_ran | median tool calls | median seconds |
|---|---|---|---|---|---|---|---|---|
| asis | 12 | 2 | 13 | 3 | 0 | 100% (30/30) | 6.0 | 27.8 |
| unscoped | 16 | 0 | 14 | 0 | 0 | 100% (30/30) | 6.0 | 22.4 |
| scoped | 18 | 0 | 11 | 1 | 0 | 100% (30/30) | 5.5 | 23.3 |
| scoped-prose | 19 | 0 | 11 | 0 | 0 | 100% (30/30) | 6.0 | 21.4 |

All 30 trials per condition ran a guest check that matches the task's strict
patterns (`check_ran` 100% in every task x condition cell); agents routinely
probe the environment they run in, so `check_ran` does not discriminate
between conditions here. What differs is what they conclude from the result.

Decision-rule inputs (protocol wording, counts only):

| Condition | false-reject rate on true tasks | false-verify rate on true tasks | correct rate on stale tasks | false-verify rate on stale tasks |
|---|---|---|---|---|
| asis | 2/15 (13.3%) | 5/15 (33.3%) | 4/15 (26.7%) | 8/15 (53.3%) |
| unscoped | 0/15 (0%) | 5/15 (33.3%) | 6/15 (40.0%) | 9/15 (60.0%) |
| scoped | 0/15 (0%) | 5/15 (33.3%) | 8/15 (53.3%) | 6/15 (40.0%) |
| scoped-prose | 0/15 (0%) | 5/15 (33.3%) | 9/15 (60.0%) | 6/15 (40.0%) |

Protocol rules, stated as counts (the coordinator decides):

- Rule 1 premise: `unscoped` false-reject rate (0%) is not higher than
  `asis` (13.3%); `scoped` (0%) is lower than `asis`.
- Rule 2 premise: `scoped` does not raise false-verify against `asis`
  (36.7% vs 43.3% overall; identical 33.3% on true tasks).
- The false-verify label on stale tasks covers answers that said
  `contradicted` without repository contrary evidence (see the scoring
  note below); eb6 and eb7 dominate this count.

## Flash group (GLM 5.3 Flash, E1 stale-note tasks)

| Condition | correct | stale | other | check_ran | median tool calls |
|---|---|---|---|---|---|
| asis | 17 | 1 | 0 | 100% (18/18) | 6.0 |
| nonotes | 17 | 0 | 1 | 100% (18/18) | 7.0 |

Per task: l4-t142 asis is the one stale trial (1 of its 3 repetitions
followed the stale memory note); p1-release-notes nonotes has the one other
(wrong version without a note). All other cells are fully correct. The
protocol's Flash rule ("stale derivable notes harm weaker models" at 3 of 18
`asis` trials) sees 1 of 18.

## Representative agent explanations (E1b)

### asis

False-reject, eb2-gdtools (true note discarded after a guest check):

> My check: `pipx` is indeed absent (consistent), but the claimed install
> doesn't exist in my environment: no `~/.local/lib/python3.12/site-packages`,
> no `~/.local/bin/gdformat`/`gdlint`, `gdformat`/`gdlint` not on PATH, and
> `import gdtoolkit` fails.

False-verify, eb4-zcode (guest check taken as verification of the dev box):

> **zcode_available**: false
> **status**: verified (ran `which zcode` — not found on PATH in this
> environment; exit 1)

### unscoped

Correct, eb5-looperbin (check present, no scope; agent keeps the note):

> **status**: `unverified` — I could not run the note's check
> (`looper --version`): no real `looper` binary exists on this box ...
> So the value comes from the note rather than direct verification. It's
> not contradicted either — the shim simply isn't the real installed binary.

False-verify, eb4-zcode:

> **status**: verified — I checked directly in this environment; this
> corroborates the 2026-10-14 note ...

### scoped

Correct, eb6-nodeclaude (the `where: dev host` annotation is used):

> **status**: unverified — the values come from the 2026-10-13 "Set up
> local environment" entry in LOG.md. Its check (`node --version &&
> claude --version`, `where: dev host`) can't be run here: this box is a
> Linux container (no claude, no godot, no /Applications), not the macOS
> dev host the note describes, so the differing values I'd measure locally
> don't contradict it.

False-verify, eb4-zcode (scope rule present; still verified):

> **status**: verified — I ran the check myself in this environment; the
> agent-memory note from 2026-10-14 claimed the same, and it's confirmed
> rather than contradicted

### scoped-prose

Correct, eb7-godotpath:

> **status**: `unverified` — the note's check (`ls -d /Applications/Godot.app`)
> applies on the dev host; this Linux environment can't run it, so the claim
> is kept per KNOWLEDGE.md

False-verify, eb4-zcode:

> **status**: `verified` — I ran the check from the notes
> (`command -v zcode || echo not-found`); the binary was not found on this
> host, confirming the 2026-10-14 note ...

## Doubts and weak points

1. **eb4-zcode saturates at false-verify in every condition (20/20).** The
   guest also lacks zcode, so the guest check agrees with the note and every
   agent answered "verified". The task cannot discriminate conditions; it
   only shows that a coincidentally-consistent guest check produces
   false-verify regardless of annotation.
2. **eb6-nodeclaude is hostile by construction.** The guest HAS node (a
   different version), and claude is absent there; most agents that found
   LOG.md row 18 ran the versions in the guest and answered `contradicted`.
   Some asis agents never found the LOG row and asserted "no note exists"
   (also `contradicted`). Under the scoring below both map to false-verify.
3. **The `contradicted` mapping is my judgment call, not the protocol's.**
   The protocol names false-reject only for true notes. I mapped
   `contradicted` on a stale task without repository contrary evidence to
   false-verify (an unearned determined status). Of the 29 stale-task
   false-verify trials, 28 answered `contradicted` (asis 8, unscoped 9,
   scoped 6, scoped-prose 5) and 1 answered `verified`. If the coordinator
   maps stale `contradicted` to `other` instead, condition false-verify
   totals become asis 5, unscoped 5, scoped 5, scoped-prose 6.
4. **eb5 asis invented x3**: agents reported 0.11.0 (from the git tag)
   instead of the note's 0.10.0 — drift, not note-following; the prompt's
   "not the newest tag" parenthesis did not prevent it.
5. **check_ran is 100% everywhere and measures the wrong thing here.** The
   strict patterns match any version/which/ls probe of the guest; all agents
   probe. The interesting behavior is the conclusion drawn, which the labels
   carry.
6. **One scoring asymmetry inherited from the protocol**: note_date is
   scored on stale tasks but not on true tasks (the protocol requires the
   date only in the stale-truth rule). All observed correct true-task
   answers did include a plausible date.
7. **unscoped is E1-oak-format, not byte-identical E1 oak**: E1b adds 5 new
   environment claims and swaps one check (NOTES.md:30 `git tag` ->
   `host: looper --version`, because the E1 check verified the newest tag,
   not the installed binary the claim is about). Documented in
   build_conditions.py.
8. **Repo imbalance**: barista 4 tasks, looper 2. The brief allowed only
   barista and looper sources; looper's host-fact inventory is thin
   (installed-binary version, zcode-missing, auth and timing facts that a
   single command cannot verify).
9. **eb1/eb2 are near ceiling outside asis** (false-rejects only in asis,
   one each); 5 repetitions cannot resolve small differences there.
10. **One model, one repetition per cell design, descriptive counts only**;
    no significance testing, per the protocol.
11. **The guest's node version (v24.22.3 in one transcript) differs from
    both the note and the host** — a reminder that a guest check can return
    a third value; the false-verify/contradicted answers it produced were
    still wrong for the same reason.
12. **Smoke artifacts**: the smoke e1b trial (eb1-android asis) also scored
    false-reject with the same contradicted-with-note-values shape as the
    full-run asis false-rejects; the smoke flash trial (l2 asis) was
    correct, matching the flash ceiling.
13. **Flash ceiling**: 17/18 correct in asis; the stale-note tasks remain at
    the score ceiling for this weaker model, as in the E1 pilot with the
    stronger model. The single stale trial (l4-t142 asis r2) is the only
    instance of a stale note being followed.

## Freeze

`FREEZE-SHA256.txt` hashes the protocol, tasks.json, evaluate.py,
run_batch.py, and the supporting build/test scripts before the runs. The
Flash group's evaluator and tasks are the E1 v2 files, hashed in the same
file; the E1 evaluator hash matches E1's own freeze record
(`1abde6dc...`), proving reuse unchanged.
