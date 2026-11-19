# OAK-Bench calibration

Date: 2026-11-19.

The calibration used GLM 5.3 with low thinking in host Pi and a fresh
Gondolin guest for each session. The guest project contained simulated
exports only. We compared all four conditions on an active withdrawal
and a restored approval. We also tried a separate authority and scope
case with plain notes plus reading rules and with OAK v0.4.

## Results

| Condition | Active withdrawal | Restored approval | Authority and scope |
|---|---|---|---|
| No notes | Fail | Fail | No run |
| Plain Markdown | Pass | Pass | No run |
| Plain Markdown with R4–R6 | Pass | Fail | Pass |
| OAK v0.4 | Timeout, recovery passed | Pass | Pass |

Both no-notes runs left both exports disabled. For restored approval,
the rules arm preserved the owner's approval in its notes. The final
agent cited R4 and used the disabled configuration to decide whether
exports were permitted. It set the production delay to 45 minutes and
left both exports disabled. The notes had also mixed verified deployment
settings with decisions during maintenance. The failure shows a specific
way a source-checking rule can be overapplied. One run cannot estimate
how often it occurs.

OAK used 40 tool calls against 28 for plain notes with rules in restored
approval, and 48 against 24 in the authority case. These are individual
trajectory counts. The sample supports further testing of the failure
mode. It gives no stable ranking among note conventions.

## Checkpoint probes

- Adding a deployment-versus-approval clarification at read time did not
  fix the restored-approval run. The authority case still passed with
  that clarification.
- Adding the distinction when the agent wrote the note also did not fix
  the restored-approval run. The resulting note preserved the approval
  and expressly said the disabled flags did not revoke it. The final
  agent still interpreted those flags as an owner-only control. This
  replay also removed the need for a scratch test, so it was a diagnostic
  probe with two changes.

- Explicitly assigning the configuration change to the final agent
  passed from the original checkpoint. The prompt asked it to set both
  enable flags according to the recorded approvals. It left the approval
  facts in the notes. This result suggests that delegated task scope
  contributed to the failure. A single replay cannot establish causality.

## What the scorer measures

A pass requires correct final settings, the expected output files, and
a matching action trace. The trace records enabled exports before the
exporter writes its output. The host resets test outputs between sessions
and keeps the raw snapshots. The trace lives in the guest, so we also
reviewed the final Pi tool calls.

The withdrawal and authority cases showed a distinction the aggregate
score hides. Agents invoked disabled exports as checks. The exporter
rejected them before producing output. Future cases should capture
attempts before the permission check and define whether an attempt
itself fails the task. Record this metric separately from completed
exports.

## Reproduction and limits

Use the [fixture and runner instructions](../oak-eval/oak-bench/README.md).
The two Riverport variants share the first two events. Treat them as
variants of one history. Maplewood is a separate development case.
Every condition ran once per case. These data describe this model and
setup. A model comparison and independent replication remain open.

The withdrawal OAK arm timed out during a recursive scratch copy in
session 3. Its recovery started from the checkpoint before that session
and added guidance to inspect the documentation inputs without running
an export test. Keep the timeout as the original outcome and report the
recovery separately.


## Run artifacts

- [Calibration summary](/home/agent/oak-experiments/oak-bench-calibration.RJL35k/summary.json)
- [Authority case summary](/home/agent/oak-experiments/oak-bench-challenge/summary.json)
- [OAK withdrawal recovery score](/home/agent/oak-experiments/oak-bench-calibration.RJL35k/handoff-oak/recovery-score.json)
- [Reader clarification score](/home/agent/oak-experiments/oak-bench-calibration.RJL35k/clarification/score.json)
- [Writer clarification score](/home/agent/oak-experiments/oak-bench-calibration.RJL35k/write-clarification-final/score.json)
- [Explicit task scope score](/home/agent/oak-experiments/oak-bench-calibration.RJL35k/explicit-task-scope/score.json)

## Maintenance handoff follow-up

With explicit task authority and the same reading rules, OAK passed
the simulated action checks and plain notes failed. The plain notes
misclassified the active approval as superseded after checking the
disabled config. OAK retained the decision through condensation, but
the agent replaced the original dated record. It also invoked the
disabled production export as a check. The simulator blocked it.
OAK used 43 tool calls against 20 for plain notes. This is one paired
trial. [Run notes](/notes/2026-11-19-oak-bench-maintenance.md)

## Structured Markdown follow-up

Plain Markdown passed both Riverport replays after the writing prompt
gave decisions and observed settings separate sections and asked for
the source, scope, reason, and history. In the Maplewood maintenance
variant, both OAK and structured Markdown passed. Structured Markdown
used 22 tool calls and OAK used 32. The simulator blocked a forbidden
export invocation in each of the four runs. Use this stronger baseline
in future comparisons. This result covers one model family and two
development histories. [Run notes](/notes/2026-11-19-oak-bench-structured-notes.md)

## Concurrent decision handoff

Two independent GLM writers recorded distinct decisions. The shared
structured Markdown file produced one Git conflict. A resolver kept
both decisions. Separate plain Markdown and separate OAK records
merged directly. All three readers applied the settings and cited
both sources and reasons. This one case isolates file layout from
OAK metadata. [Results](/notes/2026-11-19-oak-bench-concurrent-handoff.md)
