# E1b check scope results

Date: 2026-11-19. 156 trials, all completed: 120 scope trials (6 tasks × 4
conditions × 5 repetitions) with GLM 5.3, and 36 trials with GLM 5.3 Flash.
[Protocol](e1b-check-scope-protocol.md). Worker report and data:
`~/oak-experiments/e1b-scope-20261118/RESULTS.md`.

Each task asked about a fact on the dev host that the guest cannot check.
Three facts were still true and three were stale. A correct answer gives the
note value with status `unverified` and the note's date.

## Results

| Condition | Correct | False reject | False verify | Invented |
|---|---|---|---|---|
| `asis` | 12/30 | 2 | 13 | 3 |
| `unscoped` | 16/30 | 0 | 14 | 0 |
| `scoped` | 18/30 | 0 | 11 | 1 |
| `scoped-prose` | 19/30 | 0 | 11 | 0 |

With GLM 5.3 Flash on the six E1 stale-note tasks, `asis` followed a stale
note in 1 of 18 trials. `nonotes` gave 1 other answer in 18 trials.

## Findings

- **The E1 false rejection did not replicate.** In E1, one agent discarded
  a true note after its check failed. Here, no annotated condition rejected
  a true note. The prompts in this test offered an `unverified` status. With
  a word for "not checked here", agents kept the note.
- **Agents confuse their own environment with the one the note
  describes.** In 11 to 14 of 30 trials per condition, an agent ran a check
  in its sandbox and called a claim about the dev host `verified` or
  `contradicted`. Task `eb4` failed this way in all 20 trials.
- **A scope helps a little.** `where: dev host` raised correct answers from
  12 to 18 of 30 against `asis`. The scope did not stop most false
  verifications.
- **YAML and prose tied again:** 18 and 19 of 30.
- **Stale derivable notes do not mislead the weaker model much.** 1 of 18
  trials is below the protocol's threshold of 3.

## Limits

- Six tasks from two repositories. Treat the per-task counts as
  descriptive.
- `contradicted` answers on stale tasks count as false verify. The agent
  measured a different environment, so the evidence did not apply to the
  claim.
- The status vocabulary in the prompt is itself an intervention. This test
  cannot separate its effect from the annotations.

## Implication for v0.4

- Define three verification states for reports and notes: verified here,
  unverified since a date, and contradicted by evidence that applies.
- Give claims about an environment a scope, and define the scope as part of
  the claim's meaning. A check outside the scope verifies nothing.
- Keep `check` optional. The evidence does not show that it helps beyond the
  date and the scope.
