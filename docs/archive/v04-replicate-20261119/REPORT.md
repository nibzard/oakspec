# Same-batch replication of the v0.4 reading-rule result

Date: 2026-11-19 (runs finished 2026-11-18 UTC 21:02..21:20). 90 trials
in `~/oak-experiments/v04-replicate-20261119/`: 6 tasks x 3
conditions x 5 repetitions, one seeded shuffle (seed 20261120) over all
90, concurrency 2. Model zai glm-5.3, thinking low, E1 v2 guest image
(git, jq, HTTP blocked). Every trial produced a result: 59 `valid`,
31 `invalid_candidate`, no timeouts, no agent failures, no missing
trials; failed-trial counts are 0 for every condition. All inputs were
hashed into `FREEZE-SHA256.txt` before the batch ran and re-verified
after it: all 6,671 workspace entries unchanged; the runner, guest-image
manifest, and draft hashes (external provenance) also unchanged.

Conditions, all built fresh from the E1b condition trees:

- `asis`: byte copy of the E1b asis tree, unchanged.
- `scoped`: byte copy of the E1b scoped tree, unchanged.
- `v04`: the E1b scoped tree with the KNOWLEDGE.md rule text replaced
  by the lead sentence plus R4, R5, R6 from the current draft.

`diffcheck-result.json` proves: asis and scoped are byte-identical to
the E1b originals; v04 differs from scoped in KNOWLEDGE.md only, and by
exactly the rule swap. `tasks.json` and `evaluate.py` are byte copies of
E1b's (sha256 `90a67b16...`, `dd455e3a...`, equal to E1b's own freeze
record); `test_evaluate.py` passes 51/51. The draft changed since Check
A: R6 gained its final sentence. Draft sha256 at build time
`f7b63aaeb16feea5313b38f45078a453105d7f607b031c7c3d94002e05ccfb37`.

## Label counts per condition

| Condition | correct | false-reject | false-verify | invented | other | check_ran | median tool calls | median s |
|---|---|---|---|---|---|---|---|---|
| asis | 12/30 | 1 | 14 | 3 | 0 | 100% (30/30) | 6.0 | 21.2 |
| scoped | 19/30 | 0 | 11 | 0 | 0 | 100% (30/30) | 6.0 | 21.5 |
| v04 | 28/30 | 0 | 2 | 0 | 0 | 97% (29/30) | 5.0 | 19.2 |

Answered-status split inside the labels (counts only): asis
false-verify = 5 `verified` + 9 `contradicted`; scoped = 6 `verified` +
5 `contradicted`; v04 = 0 `verified` + 2 `contradicted` (both eb7). The
one asis false-reject answered `contradicted`. All 3 asis invented
answers are eb5 with status `unverified` (2 answers of 0.11.0 from a
later record, 1 answer of `0.9.1-dev.12 (3e52b5e)` from an older NOTES.md
line).

The single trial without a strict guest check (eb2-gdtools v04 r1,
correct) ran only `cat KNOWLEDGE.md; ls` and a grep of the notes for
the tool names (`grep -E 'gdtoolkit|gdformat|pipx'`); the loose flag
matched that grep command itself.

Prior-run numbers, different runs shown for comparison only (not
same-batch): E1b (seed 20261118, 2026-11-19) asis 12/30 correct,
2 false-reject, 13 false-verify, 3 invented; scoped 18/30, 0, 11, 1.
Check A v04 (seed 20261119, 2026-11-19, old R6 text) 28/30 correct,
0, 0, 2 invented.

## Label counts per task x condition

| Task (type) | Condition | correct | false-reject | false-verify | invented | other |
|---|---|---|---|---|---|---|
| eb1-android (true) | asis | 5 | 0 | 0 | 0 | 0 |
| eb1-android (true) | scoped | 5 | 0 | 0 | 0 | 0 |
| eb1-android (true) | v04 | 5 | 0 | 0 | 0 | 0 |
| eb2-gdtools (true) | asis | 4 | 1 | 0 | 0 | 0 |
| eb2-gdtools (true) | scoped | 5 | 0 | 0 | 0 | 0 |
| eb2-gdtools (true) | v04 | 5 | 0 | 0 | 0 | 0 |
| eb4-zcode (true) | asis | 0 | 0 | 5 | 0 | 0 |
| eb4-zcode (true) | scoped | 0 | 0 | 5 | 0 | 0 |
| eb4-zcode (true) | v04 | 5 | 0 | 0 | 0 | 0 |
| eb5-looperbin (stale) | asis | 2 | 0 | 0 | 3 | 0 |
| eb5-looperbin (stale) | scoped | 5 | 0 | 0 | 0 | 0 |
| eb5-looperbin (stale) | v04 | 5 | 0 | 0 | 0 | 0 |
| eb6-nodeclaude (stale) | asis | 1 | 0 | 4 | 0 | 0 |
| eb6-nodeclaude (stale) | scoped | 1 | 0 | 4 | 0 | 0 |
| eb6-nodeclaude (stale) | v04 | 5 | 0 | 0 | 0 | 0 |
| eb7-godotpath (stale) | asis | 0 | 0 | 5 | 0 | 0 |
| eb7-godotpath (stale) | scoped | 3 | 0 | 2 | 0 | 0 |
| eb7-godotpath (stale) | v04 | 3 | 0 | 2 | 0 | 0 |

Shapes behind two cells (counts only): eb6 scoped r1 answered the
guest-measured values (node `24.22.3`, claude empty) with status
`verified`; eb6 scoped r2/r3/r5 and eb7 v04 r2/r5 kept the note values
but answered `contradicted`.

## Secondary count: value-correct (status ignored)

Value-correct = every value field matches the note value, whatever the
status. The E1b key labels most such trials by status; this column
ignores status.

| Condition | value-correct | of which already labeled correct | eb5 0.11.0 from later record |
|---|---|---|---|
| asis | 27/30 | 12 | 2 |
| scoped | 29/30 | 19 | 0 |
| v04 | 30/30 | 28 | 0 |

Trials that are value-correct but not labeled correct: asis 15 (the 1
false-reject and all 14 false-verify, each keeping the note values);
scoped 10 (false-verify with note values); v04 2 (eb7 `contradicted`
with note values). Not value-correct: asis 3 (the three eb5 value
drifts), scoped 1 (eb6 scoped r1, guest values), v04 0.

### eb5 answers of 0.11.0 sourced from a later record

Three eb5 trials answered a value other than the note's 0.10.0, all in
asis, all status `unverified`:

- r3, r4: 0.11.0, note_date 2026-11-15, credited here. Each final
  message cites `.agent-memory/looper-operator-workflows-implementation.md`
  (2026-11-15: "v0.11.0 ... `make install` run") as superseding the
  annotated NOTES.md 0.10.0 claim. 0.11.0 is the host truth today.
- r1: `0.9.1-dev.12 (3e52b5e)` from an older NOTES.md line (line 129),
  note_date 2026-11-13. Not credited (a different, older record, and a
  wrong value today).

## The R4-R6 text used

Extracted verbatim from `~/oak/docs/oak-0001-v0.4-draft.txt`
Section 6.1 at build time; the 2-space section margin was dropped, the
wording is untouched. Identical in both v04 KNOWLEDGE.md files after the
lead sentence "Memory follows OAK-0001 v0.4; the rules are below.":

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

The last R6 sentence is new since Check A; that is the only change in
this block between the two runs (diffed against Check A's built
condition).

## Doubts

1. 5 repetitions per cell; all counts are descriptive, no significance
   testing.
2. Model non-determinism across runs remains: this batch's asis and
   scoped counts differ in detail from E1b's (asis correct is 12 in
   both, but false-reject is 1 vs 2; scoped correct is 19 vs 18)
   although the trees are byte-identical. The same-batch design removes
   the cross-run-day confound for the v04-vs-scoped comparison, not
   run-to-run variance.
3. The E1b evaluator's mapping of stale `contradicted` without
   repository contrary evidence to false-verify is an inherited judgment
   call, documented in evaluate.py; it covers 9 (asis), 5 (scoped), and
   2 (v04) of the false-verify counts above.
4. The eb5 "later record" credit is a manual read of 3 transcripts (the
   final messages cited above); the auto-flag in analyze.py greps the
   transcript and I verified each by hand. Two trials credited, one not.
5. value-correct ignores both status and note_date; a trial that keeps
   values but gives a wrong date would still count. No such trial
   occurred (no `other` labels at all).
6. check_ran only detects strict command patterns in the guest; the one
   v04 trial without them only grepped the notes (the loose flag
   matched the grep pattern itself). E1b already noted that all agents
   probe; the measure does not discriminate.
7. eb4-zcode's 0/5 under asis and scoped versus 5/5 under v04 rests on
   5 repetitions of one task whose guest check agrees with the note.
8. The v04 text differs from Check A's v04 (the new R6 sentence), so
   this batch re-tests the condition as it now reads, not the exact
   Check A stimulus.
9. Smoke (2 trials) ran before the freeze, E1b-style; the batch's 90
   trials all ran after it. `analyze.py`, `learnings.md`, this report,
   and `analyze-output.txt` are working outputs, not trial inputs, and
   are not in the freeze.
10. `analyze-output.txt`, `batch.log`, `smoke/`, and `runs/` were written
    by the runs themselves; everything hashed in FREEZE-SHA256.txt was
    verified unchanged after the batch.
