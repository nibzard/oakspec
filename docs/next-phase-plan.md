# Next phase: ground OAK in real memory failures

Planning date: 2026-11-18. This plan replaces the broad comparison in days
5–7 of the [v0.4 timeline](v0.4-timeline.md). The earlier pilots reached the
score ceiling. The plan follows the timeline's own rule to revise the cases
before scaling up.

## Evidence behind this plan

- Five studies found no correctness difference between OAK and prose or
  control. [Papercut](../report.md),
  [metadata pilot](metadata-prose-pilot-results.md),
  [longitudinal pilot](longitudinal-pilot-results.md).
- The Papercut tool-call reduction did not appear when only the metadata
  changed. The index or the curation probably caused it.
- An audit of papercut, looper, and barista memory found 46 verified
  defects. Most were true when written and went stale after a later event.
- Mining 700 user corrections in ohya found 12 memory failures. Lost
  decisions and stale tool workflows caused most of them.
- Details: [real memory failures](/notes/2026-11-18-oak-real-memory-failures.md).

## Position

1. Code is the memory for the current state. Agents re-derive it cheaply.
   Notes that copy derivable state rot first.
2. Notes earn their place for facts that cannot be re-derived: decisions
   and reasons, approvals, revocations, facts about the machine, and
   ownership of work in progress.
3. The write path loses knowledge. Memory written in an unmerged worktree is
   lost. A controller re-import can revert verified edits. A format cannot
   fix this.
4. A date makes staleness visible but does not prevent it. A `check`
   pointer, a command or source that re-verifies the claim, turns staleness
   into an action that an agent can run.

The proposed OAK thesis: keep what cannot be re-derived. Point to what can,
with a check.

Revised 2026-11-19 after E1, E1b, and the candidate checks: agents verify
derivable state without being told, so `check` pointers added little. The
main risk is confusing environments. Short reading rules (v0.4 R4 to R6)
fixed most of that, and metadata fixed less. The thesis is now: keep what
cannot be re-derived, point to what can, and say where a claim applies.

## Progress, 2026-11-19

| Item | State | Result |
|---|---|---|
| E1 rot benchmark pilot | Done | [Stale derivable notes caused no stale actions](e1-rot-pilot-results.md) |
| E1b check scope and Flash group | Done | [Agents confuse environments; a scope helps a little](e1b-check-scope-results.md) |
| E3 parallel writes | Done | [No loss through merges; append costs less](e3-parallel-writes-results.md) |
| E2 decision loss | Not started | E1 suggests that notes matter only for facts that cannot be re-derived |
| E4 check cost | Folded into E1b | Agents probe their own environment anyway |
| v0.4 draft | [Candidate](../publish/oak-0001.txt) | [R4 to R6 replicated, and they work without metadata](v04-candidate-results.md) |

## Experiments

| ID | Name | Question | Conditions |
|---|---|---|---|
| E1 | Rot benchmark | Do notes about the current state help or hurt on real repositories? | As-is notes, no notes, OAK v0.4 with `check`, equivalent prose |
| E2 | Decision loss | Does the representation matter when the note is the only record? | Factorial from `research.md`, built from the 12 mined cases |
| E3 | Parallel writes | Which write pattern loses the fewest records across worktrees? | One shared file, append-only dated records, one file per claim |
| E4 | Check cost | Do agents run `check` pointers, and what does it cost? | With and without `check`, measured inside E1 |

Rules for every experiment:

- Freeze and hash the protocol before the runs.
- Score deterministically. Blind any manual review.
- Treat each trajectory or independent task run as the unit.
- Keep failed and timed-out trials in the results.
- Keep answer keys outside the guest.

Run E1 first. If the no-notes condition wins, notes about the current state
should go, and the v0.4 draft should say so.

## RFC v0.4 direction

- Conformance by meaning. A note conforms if it states the core facts.
  YAML front matter and plain sentences are both valid encodings.
- Core concepts: kind, event date, verification date, origin, replacement,
  revocation, and scope (`where`). `check` became an open question.
- Rule: do not copy derivable state. Point to its source.
- Write-path guidance: append dated records. Do not overwrite the current
  state from a stale branch or an old import.
- A verification date records an actual check. Never write a guessed date.
- Move layout, `index.md`, journals, and setup rituals to a companion guide.
- Keep v0.3 files valid.

## Later work

- Dogfood v0.4 on one project after approval. Re-run the auditor every few
  days and track the rot rate over two weeks.
- Publish an evidence page on oakspec.dev with every result, including
  null results. Publish after approval.
- Seek two independent integrations only after the evidence exists.

## Roles

GLM 5.3 workers through `claude-zai -p` build fixtures, run trials, and
draft text. Pi with Gondolin runs the agent sessions under test. The
coordinator sets protocols, reviews results, and decides.

## Follow-up outside OAK

The barista audit reported that a looper controller re-import reverted
verified backlog edits. Investigation on 2026-11-19 corrected this: nothing
reverted. A worker edited the worktree copy of `to-do.json`, which looper
excludes from result commits, and the worktree was deleted at acceptance.
The edit never reached the live file. Fix: branch
`fix/backlog-reimport-revert` in `~/looper-fix-reimport` (commit `e760c94`).
Report: `~/oak-experiments/looper-fix-REPORT.md`. This is the W9 failure:
a note that never reaches the shared copy is lost.
