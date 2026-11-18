# E3 parallel writes pilot results

Date: 2026-11-18. 36 rounds: 4 scenarios × 3 layouts × 3 repetitions. Each
round ran three concurrent writer sessions in separate worktrees, a fixed
merge order with a resolver session after each conflict, and a fresh reader.
Model: GLM 5.3 at low thinking with the git-enabled Gondolin guest.
[Protocol](e3-parallel-writes-protocol.md). Data:
`~/oak-experiments/e3-writes-20261118/pilot/`.

## Results

| Layout | Lost records | Stale overwrites | Merge conflicts | Resolver tool calls | Mean round time |
|---|---|---|---|---|---|
| `append` | 0 | 0 | 6 | 45 | 52 s |
| `shared` | 0 | 0 | 24 | 94 | 107 s |
| `oak-index` | 0 | 0 | 24 | 84 | 230 s |

Reader answers were correct in 70 of 72 questions for `append`, 71 of 72 for
`shared`, and 72 of 72 for `oak-index`.

35 of 36 rounds completed normally. One `oak-index` round had a session
failure and took 1,597 seconds. Its records and reader answers were still
complete.

## Findings

- **No layout lost records through `git merge`.** The resolvers kept every
  decision. Under the protocol's rule, this is a null result. The merge path
  does not need a rule in the specification.
- **Append-only records cost much less.** `append` had a quarter of the
  conflicts of the other layouts and the shortest rounds. `oak-index` rounds
  took about 4.4 times as long as `append`, because writers updated both a
  topic file and the index.
- **The frozen score shows "wrong current" for `output-name` in all nine
  marksweep rounds, in every layout.** Manual review of a sample found the
  correct replacing record and matching code. This is a scorer artifact. The
  frozen scores keep it.

## Limits

- The test covered loss through `git merge` only. The audit's real loss
  paths were different: branches that never merged, and an import that
  overwrote files outside git. This pilot did not test either.
- The resolvers were capable and careful. A weaker resolver or an automatic
  merge strategy could lose records.
- The `output-name` artifact means that the `wrong_current` counts are not
  meaningful. The lost-record counts do not depend on that rule.

## Implication for v0.4

Recommend append-only dated records as the default write pattern, because
they cost less. Do not claim that they prevent loss. Treat unmerged branches
and overwriting imports as host and tool responsibilities. State that a
record exists only after it reaches the shared branch.
