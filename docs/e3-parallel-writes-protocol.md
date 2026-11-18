# E3 parallel writes protocol

Status: draft, 2026-11-18. Freeze this file and hash it before the pilot.
Plan: [next phase](next-phase-plan.md).

## Question

When several agents work at the same time in separate git worktrees, which
note layout loses the fewest records after the branches merge? The audit found
two real loss paths: memory left in unmerged worktrees, and a stale import that
overwrote verified edits.

## Layouts

| Layout | Writers do this |
|---|---|
| `shared` | Update one `NOTES.md`, including its "Current state" section |
| `oak-index` | Edit topic files in `knowledge/` and update `knowledge/index.md` (v0.3 style) |
| `append` | Add one new dated record file in `knowledge/records/`. Do not edit other files |

The same short maintenance guidance goes into every layout. Only the write
pattern differs.

## Procedure for one round

1. Start from a small project with a seeded history of six records.
2. Create three worktrees from `main`. One worktree starts from an older
   commit to simulate a stale branch.
3. Run three fresh Pi sessions at the same time, one in each worktree. Each
   session makes one code change and records one decision. Two of the decisions
   replace earlier ones.
4. Merge the branches into `main` in a fixed order with `git merge`. If a merge
   conflicts, a fresh resolver session gets the prompt "Resolve the merge
   conflicts and keep all project knowledge."
5. A fresh reader session answers six questions about the current decisions
   and their history.

## Measures

- Primary: lost records. These are decisions present on a branch but absent
  or wrong on `main` after the merge.
- Merge conflicts per round, and resolver tool calls.
- Stale overwrites: older content that replaced newer content.
- Reader accuracy on current decisions and on replaced decisions.

## Runs

- Use 4 project scenarios × 3 layouts × 3 repetitions = 36 rounds. Each round
  has 3 writer sessions, 0 or more resolver sessions, and 1 reader session.
- Use the git-enabled Gondolin guest from E1, GLM 5.3, and low thinking.
- Treat the round as the unit.

## Decision rules

- If `append` loses fewer records than `oak-index` in at least 3 of the 4
  scenarios, v0.4 recommends append-only records as the default write pattern.
- If no layout loses records, the write path does not need a rule in the
  specification. Record this as a null result.
