# Longitudinal OAK and prose pilot

Date: 2026-11-18. All 60 sessions completed. There were no timeouts,
failed processes, or manual repairs to project files during the runs.

## Results

| Measure | OAK | Prose |
|---|---|---|
| Correct checked operational settings | 30/30 sessions | 30/30 sessions |
| Correct reported approver | 30/30 | 30/30 |
| Correct reported verification date | 30/30 | 30/30 |
| Correct reported approval date against frozen key | 26/30 | 30/30 |
| Raw frozen checks passed | 239/270 | 245/270 |
| Tool calls | 180 | 192 |
| Sum of session elapsed seconds | 738.4 | 805.1 |

Operational settings include the export format and compression, backup
retention and local-only setting, and public channel and support method.
Manual review of all 20 documentation snapshots confirmed that the visible
wording agreed with the publication markers. The service and backup programs
remained unchanged in all snapshots.

Both conditions retained completed task state in meaning. Both service
trajectories used `done` instead of the key's `complete`. This accounts for
20 raw failed checks across the two conditions. The prompt did not define
the allowed completion strings. These failures do not demonstrate reopened
or unfinished work.

## Findings from the notes

- The OAK service note lost its opening front-matter delimiter in sessions
  3 through 9. Session 10 restored it. The settings remained correct while
  the metadata representation was broken.
- The OAK backup trajectory reported February 17 as the approval date for
  21-day retention in sessions 5 through 8. The key expects February 21,
  when Omar resolved the conflicting notes and explicitly approved 21 days.
  An earlier 21-day note really was dated February 17. This is a distinction
  between an earlier assertion and its later confirmation, not an invented
  date. The frozen score retains the four failures.
- The OAK backup notes treated unapproved vendor advice as an unresolved
  conflict requiring an owner decision. The prose documentation trajectory
  similarly described unapproved marketing copy as a conflict. Both still
  followed the approved project settings. Conflict reporting needs a clearer
  definition before it serves as a performance measure.
- All six final notes retained the main decision history and task completion.
  The documentation notes also kept the withdrawn approval and re-approval.
  Some notes accumulated old present-tense statements alongside later updates.
  Readers still had to interpret the history to identify current state.

## Scoring limits

The frozen key expects `open_tasks` to contain only task IDs from tasks.json.
The prompt asks for an open-task list without defining that restriction.
Agents also listed pending approvals or conflict resolution as open work.
That mismatch affects 16 OAK checks and 8 prose checks. Keep these raw results,
but do not interpret all such failures as lost task state.

One OAK and seven prose conflict flags differed from the key. The key treats
unsupported recommendations as proposals, with an unresolved conflict only
when the two owner notes disagree. The general word conflict in the prompt
allowed a broader reading. Operational settings provide the clearer measure
in this run.

The three histories supply only three paired trajectories. The 60 sessions
are dependent within those trajectories. This pilot supports no claim of
statistical significance or equivalence. The lower OAK tool count is an
observation from this run.

Completed task status was checked after each session. Repeated work itself
was not independently instrumented, so this run cannot quantify repeated
completed work from task state alone.

## Execution and reproduction

The [fixtures and procedure](../oak-eval/longitudinal/README.md) used three
histories with ten sessions each and two conditions. Initial project facts
and maintenance instructions were shared. Only the maintained note's initial
metadata representation differed. Both conditions could search the same
evidence files and received explicit maintenance guidance each session.
This tests that representation difference under those conditions.

The runner used host Pi 1.5.2, GLM 5.3, low thinking, and Gondolin 0.14.0
with the tested extension and an empty guest HTTP allowlist. Each session
started a fresh process and guest. Configuration discovery, other extensions,
MCP servers, and skills were disabled. Model requests remained on the host.
Provider-side tools were outside the guest network policy.

The six trajectories ran in a seeded randomized order with concurrency two.
The runner saved the protocol and SHA-256 hashes before execution. The
copied input hashes were verified afterward. Scoring remained frozen.
Manual review was conducted with condition labels visible.

Durable artifacts are in
`/home/agent/oak-experiments/longitudinal-20261118/`.
They include the protocol, copied inputs, prompts, event logs, scores,
per-session project snapshots, `results.json`, and `summary.json`. Credentials
were not copied into that results directory.

The [runner](../oak-eval/longitudinal/run.py) accepts paths for the output,
extension, Pi CLI, Node.js, and isolated Pi configuration. Its local launcher
uses this machine's agent UID and KVM group setup. The dependency installation
and credential configuration must exist before reproducing the run.

## Implication for v0.4

This pilot found no operational advantage for OAK on these histories.
It found maintenance errors and weaknesses in the measurement. Clarify
completion values, pending approvals, conflicts, and the approval-date rule
before another comparison. Keep the frozen results as evidence of both
agent behavior and test limitations. Use these findings when reviewing the
v0.4 temporal and lifecycle definitions.
