# OAK v0.4 candidate check results

Date: 2026-11-19. Candidate: [v0.4 draft](oak-0001-v0.4-draft.txt). Model:
GLM 5.3 at low thinking, Pi with the git-enabled Gondolin guest. Reports:
`~/oak-experiments/v04-checks-20261119/REPORT.md` and
`~/oak-experiments/v04-replicate-20261119/REPORT.md`.

## Reading rules R4 to R6 on the scope tasks

The six [E1b](e1b-check-scope-results.md) tasks ask about facts on the dev
host that the agent cannot check. One batch, one seed, 5 repetitions:

| Condition | Correct | False reject | False verify | Invented |
|---|---|---|---|---|
| `asis` | 12/30 | 1 | 14 | 3 |
| `scoped` | 19/30 | 0 | 11 | 0 |
| `v04` | 28/30 | 0 | 2 | 0 |

`v04` is the `scoped` tree with the `KNOWLEDGE.md` rule text replaced by R4,
R5, and R6 from the draft. Nothing else differs. An earlier run with the
previous R6 text gave the same 28 of 30.

- `v04` matched or beat `scoped` on all six tasks and beat `asis` on five.
- Task `eb4` failed in all 30 earlier `asis` and `scoped` trials. It passed
  in all 10 `v04` trials across both runs.
- Agents cited the rules: "per R5 ... a miss in a sandbox verifies nothing
  about the dev box."
- The effect comes from the rule text. The `where` annotation sat under both
  `scoped` and `v04`.

### Rules without annotations

A second batch (seed 20261121, 90 trials) added `rules-only`: the plain
`asis` notes with the same R4 to R6 text and no annotations.

| Condition | Correct | False verify | Invented |
|---|---|---|---|
| `asis` | 15/30 | 12 | 3 |
| `rules-only` | 27/30 | 2 | 1 |
| `v04` | 28/30 | 1 | 1 |

The annotations added almost nothing beyond the rules. The plain notes
already named the place in their sentences ("on the dev box"). The rules
made agents use that information.

## Setup from the draft on barista (3 trials)

- No trial lost note content or invented a date.
- 2 of 3 trials marked environment claims with `where`. The third trial's
  summary and setup record said that it did, but the files had no `where`.
- No trial replaced copied derivable state. The draft did not ask for it
  during setup.

## Edge cases (18 trials)

Deletion, revocation, and an injected instruction passed in 17 of 18
trials, with and without OAK. These cases reached the ceiling for this
model and do not separate the conditions.

## Defects fixed in the draft

1. The instruction-file step was unclear for a project with only `CLAUDE.md`.
2. Setup did not say what to do with copied derivable state.
3. The revoked template set `as_of` without a check. `as_of` now covers
   confirmation by the owner.
4. R6 did not cover the case where no note answers the question.
5. No rule covered two resources that disagree.
6. The self-check let agents report intent instead of file contents.
7. Tools must accept the short YAML form.
8. `where` values drifted between "dev host" and "dev box".

## Limits

- Six tasks from two repositories, one model family.
- The edge cases were synthetic and easy.
- The notes in these tasks already named their place in plain words. Notes
  that do not name a place may need `where` or an equivalent sentence.
