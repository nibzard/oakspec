# E1 rot benchmark pilot results

Date: 2026-11-18. 48 trials: 12 tasks × 4 conditions × 1 repetition. All
trials exited normally. Model: GLM 5.3 at low thinking, Pi 1.5.2, Gondolin
0.14.0 with a git-enabled guest and no guest HTTP access.
[Protocol](e1-rot-benchmark-protocol.md). Data:
`~/oak-experiments/e1-rot-20261118/v2/pilot/`.

## Results

| Task type | Tasks | asis | nonotes | oak | prose |
|---|---|---|---|---|---|
| Stale note | 6 | 6 correct | 6 correct | 6 correct | 6 correct |
| Note-needed (primary) | 3 | 3 correct | 2 correct, 1 stale | 2 correct, 1 stale | 2 correct, 1 stale |
| Control | 2 | 2 correct | 2 correct | 2 correct | 2 correct |
| `b5` (excluded) | 1 | correct | other | correct | correct |

Tool calls were similar across conditions.

## Findings

- **Stale notes about derivable state caused no stale actions.** In all
  24 stale-note trials, including the 6 `asis` trials with the wrong notes
  present, the agent verified the state from code, git, or data. Examples:
  the next release version, backlog counts, and whether T142 landed.
  These tasks reached the score ceiling. Notes about derivable state
  neither helped nor hurt this model.
- **Notes mattered only for facts that the agent could not check.** In
  `b2`, the Android SDK and JDK paths on the dev machine exist only in
  agent memory. `asis` answered correctly. `nonotes` could not know them.
- **The check pointer rejected a true note.** In `b2`, the `oak` and
  `prose` annotations said `check: host: ls /home/agent/Android/Sdk`. The
  agent ran in a guest, not on the dev machine, so the check failed. Both
  agents concluded that the note was stale and discarded the correct
  paths. The `asis` agent trusted the note and was right.
- **YAML and prose gave identical outcomes** in all 12 tasks.

## Limits

- One repetition per cell. Treat these results as descriptive.
- `b3` passed in `nonotes` by coincidence. The guest also has no `pipx`, so
  the agent's check in the guest matched the truth about the host.
- `p2` passed in `nonotes` because the agent reasoned from the absence of
  an approval record.
- One model. A weaker model may trust stale notes more.

## Decision

The main run of 144 trials would repeat a ceiling result on the stale-note
tasks, so it does not run as designed. Two follow-ups replace it:

1. E1b tests check scope: facts that are true or false in another
   environment and cannot be checked where the agent runs.
2. A weaker-model group runs the stale-note tasks with GLM 5.3 Flash, to
   test whether stale notes mislead a less careful agent.

Implication for v0.4: a `check` needs a scope. A failed check outside that
scope means "cannot verify here", not "false".
