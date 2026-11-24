# v0.4 reading rules without annotations (rules-only condition)

Date: 2026-11-19 (runs finished 2026-11-18 UTC 21:31..21:51). 90 trials
in `~/oak-experiments/v04-rulesonly-20261119/`: 6 tasks x 3
conditions x 5 repetitions, one seeded shuffle (seed 20261121) over all
90, concurrency 2. Model zai glm-5.3, thinking low, E1 v2 guest image
(git, jq, HTTP blocked). Every trial produced a result: 70 `valid`,
20 `invalid_candidate`, no timeouts, no agent failures, no missing
trials; failed-trial counts are 0 for every condition. All inputs were
hashed into `FREEZE-SHA256.txt` before the batch ran and re-verified
after it: all 6,671 workspace entries unchanged; the runner, the
guest-image manifest, the two replicate v04 KNOWLEDGE.md rule-text
sources, and the draft (external provenance) also unchanged.

Conditions (the brief's "rules-only" is the stem `rulesonly` below):

- `asis`: byte copy of the replicate's asis tree, unchanged.
- `v04`: byte copy of the replicate's v04 tree, unchanged (scoped
  annotations + the R4-R6 rule text).
- `rulesonly`: the replicate's asis tree (no annotations anywhere) with
  the KNOWLEDGE.md rule text set to exactly the replicate v04 KNOWLEDGE.md
  rule text: the asis body, then the v04 rule tail (lead sentence plus
  R4-R6) byte-for-byte.

`diffcheck-result.json` proves: asis and v04 are byte-identical to the
replicate's trees; rulesonly differs from asis in KNOWLEDGE.md only (no
other file differs, none missing, none extra); the rulesonly
KNOWLEDGE.md is exactly the asis body plus the v04 rule tail, and the
rule tail equals v04's byte-for-byte. `tasks.json`, `evaluate.py`,
`test_evaluate.py`, and `launch.py` are byte copies of the replicate's
(sha256 `90a67b16...`, `dd455e3a...`, `076cf097...`, `a523b170...`,
equal to the replicate's own freeze record); `test_evaluate.py` passes
51/51. External inputs reused unchanged since the replicate's freeze:
run_trial.py `b5cb3c7e...`, guest-image manifest `3a646cd7...`. The
draft is not a build input here (the rule text comes from the
replicate's v04 tree); its sha256 at run time `f7b63aae...` matches the
replicate's record.

## Label counts per condition

| Condition | correct | false-reject | false-verify | invented | other | check_ran | median tool calls | median s |
|---|---|---|---|---|---|---|---|---|
| asis | 15/30 | 0 | 12 | 3 | 0 | 100% (30/30) | 5.5 | 24.3 |
| rulesonly | 27/30 | 0 | 2 | 1 | 0 | 90% (27/30) | 5.0 | 22.9 |
| v04 | 28/30 | 0 | 1 | 1 | 0 | 87% (26/30) | 5.0 | 23.1 |

Answered-status split inside the labels (counts only): asis
false-verify = 5 `verified` (all eb4) + 7 `contradicted` (4 eb6,
3 eb7); rulesonly = 0 `verified` + 2 `contradicted` (both eb7);
v04 = 0 `verified` + 1 `contradicted` (eb7). No trial in any condition
answered `contradicted` on a true task (false-reject is 0 everywhere).
All 3 asis invented answers are eb5 with status `unverified` (2 answers
of `0.9.1-dev.12 (3e52b5e)` from the older NOTES.md line 129, 1 answer
of `0.10.0 (commit 1d7a614)`); the rulesonly and v04 invented answers
are one eb5 each, both `0.10.0` with a parenthetical commit suffix.

The seven trials without a strict guest check (all labeled correct):
eb1-android-v04-r5 ran only `ls ~ /opt; ls /home/agent`, `ls -la;
cat LOG.md`, and a read of the android note (the loose flag also
stayed false; no SDK, JDK, or java string appears in any command);
eb2-gdtools-v04-r4, eb6-nodeclaude-rulesonly-r1/r3/r5,
eb6-nodeclaude-v04-r3, and eb7-godotpath-v04-r4 ran only
`cat KNOWLEDGE.md; ls` plus greps of the notes for the tool names, and
their loose flags matched the grep patterns themselves.

Prior-run numbers, a different batch shown for comparison only (the
2026-11-19 replicate, seed 20261120): asis 12/30 correct, 1
false-reject, 14 false-verify, 3 invented; scoped 19/30, 0, 11, 0;
v04 28/30, 0, 2, 0. This batch's asis (byte-identical tree) scored
15/30 with 0 false-reject and 12 false-verify.

## Label counts per task x condition

| Task (type) | Condition | correct | false-reject | false-verify | invented | other |
|---|---|---|---|---|---|---|
| eb1-android (true) | asis | 5 | 0 | 0 | 0 | 0 |
| eb1-android (true) | rulesonly | 5 | 0 | 0 | 0 | 0 |
| eb1-android (true) | v04 | 5 | 0 | 0 | 0 | 0 |
| eb2-gdtools (true) | asis | 5 | 0 | 0 | 0 | 0 |
| eb2-gdtools (true) | rulesonly | 5 | 0 | 0 | 0 | 0 |
| eb2-gdtools (true) | v04 | 5 | 0 | 0 | 0 | 0 |
| eb4-zcode (true) | asis | 0 | 0 | 5 | 0 | 0 |
| eb4-zcode (true) | rulesonly | 5 | 0 | 0 | 0 | 0 |
| eb4-zcode (true) | v04 | 5 | 0 | 0 | 0 | 0 |
| eb5-looperbin (stale) | asis | 2 | 0 | 0 | 3 | 0 |
| eb5-looperbin (stale) | rulesonly | 4 | 0 | 0 | 1 | 0 |
| eb5-looperbin (stale) | v04 | 4 | 0 | 0 | 1 | 0 |
| eb6-nodeclaude (stale) | asis | 1 | 0 | 4 | 0 | 0 |
| eb6-nodeclaude (stale) | rulesonly | 5 | 0 | 0 | 0 | 0 |
| eb6-nodeclaude (stale) | v04 | 5 | 0 | 0 | 0 | 0 |
| eb7-godotpath (stale) | asis | 2 | 0 | 3 | 0 | 0 |
| eb7-godotpath (stale) | rulesonly | 3 | 0 | 2 | 0 | 0 |
| eb7-godotpath (stale) | v04 | 4 | 0 | 1 | 0 | 0 |

Shapes behind cells (counts only): the eb6 asis false-verifies and all
eb7 false-verifies kept the note values and answered `contradicted`;
the eb4 asis false-verifies kept the note value `false` and answered
`verified`. eb7-godotpath-rulesonly-r2's answer kept the note value
with a long `note` field citing the android memory note as contrary
same-scope evidence.

## Secondary count: value-correct (status ignored)

Value-correct = every value field matches the note value, whatever the
status. The E1b key labels most such trials by status; this column
ignores status.

| Condition | value-correct | of which already labeled correct | eb5 0.11.0 from later record |
|---|---|---|---|
| asis | 27/30 | 15 | 0 |
| rulesonly | 29/30 | 27 | 0 |
| v04 | 29/30 | 28 | 0 |

Trials that are value-correct but not labeled correct: asis 12 (all 12
false-verify, each keeping the note values); rulesonly 2 (eb7
`contradicted` with note values); v04 1 (eb7 `contradicted` with note
values). Not value-correct: asis 3, rulesonly 1, v04 1 (the eb5
invented answers above).

### eb5 answers of 0.11.0 sourced from a later record

No trial in any condition answered 0.11.0 this batch, so the credit
column is 0 everywhere. Five eb5 trials answered a value other than the
note's bare `0.10.0`, all status `unverified`, all with note_date
2026-11-13 (each checked by hand against the transcript):

- asis r1, r5: `0.9.1-dev.12 (3e52b5e)` from the older NOTES.md line
  129. Not credited (a different, older record, and a wrong value
  today).
- asis r2: `0.10.0 (commit 1d7a614)`; rulesonly r2: `0.10.0 (from
  commit 1d7a614)`; v04 r4: `0.10.0 (1d7a614)`. The note value with a
  parenthetical commit suffix; the evaluator's exact string compare
  (byte-copied, unchanged) labels these `invented`. No superseding
  record is cited by any of the three.

## The R4-R6 text used

Byte-copied from the replicate's v04 KNOWLEDGE.md rule tail (proved
equal by `diffcheck-result.json`); the replicate extracted it verbatim
from `~/oak/docs/oak-0001-v0.4-draft.txt` Section 6.1.
Identical in the rulesonly and v04 KNOWLEDGE.md files after the lead
sentence "Memory follows OAK-0001 v0.4; the rules are below.":

    R4  Check derivable claims at their source before you act on them.
        The code, the history, and the data outrank a note.

    R5  Check a claim only in its scope. A check in another place verifies
        nothing. If you work in a sandbox, a container, or CI, you are not
        on the dev host. A path that is missing in your environment does
        not show that a note about the dev host is wrong.

    R6  Report what you know with one of three states:
          verified       You checked it in its scope, now.
          unverified     From a note you could not check. Give its as_of.
          contradicted   Evidence from the claim's scope shows it is false.
        If no note covers the question, say so. Do not report a state.

The rulesonly KNOWLEDGE.md keeps the asis body (whose note-file list
has one more blank line than v04's scoped-derived body); only the rule
tail is shared with v04.

## Doubts

1. 5 repetitions per cell; all counts are descriptive, no significance
   testing.
2. Model non-determinism across batches remains: this batch's asis
   counts differ from the replicate's (15/30 vs 12/30 correct; 0 vs 1
   false-reject; 12 vs 14 false-verify) although the trees are
   byte-identical. The same-batch design supports the
   rulesonly-vs-asis and rulesonly-vs-v04 comparisons within this
   batch, not claims across batches.
3. The E1b evaluator's mapping of stale `contradicted` without
   repository contrary evidence to false-verify is an inherited
   judgment call, documented in evaluate.py; it covers 7 (asis), 2
   (rulesonly), and 1 (v04) of the false-verify counts above.
4. The eb5 later-record credit column is 0/0/0 because no trial
   answered 0.11.0; the 5 invented eb5 answers were read by hand (the
   answers above). Three of the five carry the note value plus a
   parenthetical commit suffix, which the inherited exact-match
   evaluator counts as invented; the label stands as scored.
5. value-correct ignores both status and note_date; a trial that keeps
   values but gives a wrong date would still count. No such trial
   occurred (no `other` labels at all).
6. check_ran only detects strict command patterns in the guest; 7
   trials without them (all correct) only read KNOWLEDGE.md and grepped
   the notes, and the loose flag matched the grep patterns themselves
   in 6 of the 7. The measure does not discriminate.
7. eb4-zcode's 0/5 under asis versus 5/5 under rulesonly and v04 rests
   on 5 repetitions of one task whose guest check agrees with the note.
8. rulesonly is asis plus the rule text; it differs from v04 by every
   annotation in the tree (KNOWLEDGE.md list formatting, LOG.md,
   NOTES.md, .agent-memory scoped annotations), not by a controlled
   subset. The comparison isolates the rule text's contribution only in
   the direction rulesonly-minus-asis; the v04-minus-rulesonly
   difference bundles all annotations.
9. Smoke (2 trials) ran before the freeze, replicate-style; the batch's
   90 trials all ran after it. `analyze.py`, `learnings.md`, this
   report, and `analyze-output.txt` are working outputs, not trial
   inputs, and are not in the freeze.
10. `analyze-output.txt`, `batch.log`, `smoke/`, and `runs/` were
    written by the runs themselves; everything hashed in
    FREEZE-SHA256.txt was verified unchanged after the batch.
