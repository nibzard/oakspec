# OAK-Bench plan

Planning date: 2026-11-19.

Test whether OAK v0.4 improves decisions across fresh sessions when the
project files cannot reconstruct the owner's intent. Keep the spec fixed
through the first replication. This plan follows the
[v0.4 pilots](../publish/evidence.txt) and extends the
[existing handoff runner](../oak-eval/longitudinal/README.md).

## 1. Build one hard handoff

Create a fictional export project with a simulated destination. Give one
agent the owner's initial decision, a second agent a production withdrawal,
and a third agent a staging exception. Each must do ordinary project work
and maintain the notes allowed by its condition. Start a fresh fourth
session with a request to configure the export. Include variants where
production approval holds and where a later decision restores it. Keep
source files and Git history from revealing the answer. Use task prompts
that leave verification wording to the agent.

Compare four conditions:

| Condition | What carries forward |
|---|---|
| No notes | The project and task changes |
| Plain Markdown | Good notes with free-form maintenance guidance |
| Plain Markdown with reading rules | The same notes and maintenance guidance, plus rules R4–R6 |
| OAK v0.4 | The same initial facts and reading rules, plus OAK record and maintenance conventions |

Match the path where agents start looking, the source events, task prompts,
and model settings. Let agents write their own notes after setup. The last
comparison estimates the effect of the remaining OAK practices as a package.

## 2. Calibrate and freeze the protocol

Run Pi on the host with a fresh Gondolin guest for each session. Reuse
the longitudinal runner and the tested guest setup. Pin the model and tool
versions. Check one guest boot, one project edit, and one blocked network
request. Disable unrelated host context and extensions. Carry forward only
the intended project state. Keep scorers, answer keys, and logs on the host.

Score the final configuration and simulated action log. Require the agent
to complete the permitted action and respect the current decision in each
environment. Report attribution, false verification, time, tool calls,
usage where available, and note edits separately. Review sample logs.
Record failures and timeouts. Retry infrastructure failures from the saved
predecessor in a new attempt directory.

Use two development histories across four conditions with one model
(eight trajectories, up to 32 sessions). Fix cases if every condition
passes, if the no-notes arm succeeds through leaked evidence, or if human
review and the scorer disagree. Freeze the protocol before replication.

Calibration found that the final agent can infer an owner-only control
from a disabled setting. Before freezing replication prompts, state
which settings the task delegates to the agent. Keep the approval facts
in the history. Score attempts separately from completed exports.
See the [calibration results](oak-bench-calibration.md).

## 3. Replicate across two model families

Use four unseen histories, four conditions, and two model families
(32 trajectories, up to 128 sessions). Pair conditions by history and
model. Randomize run order with a recorded seed. Keep held-out cases and
grading rules under human control. Set a spending cap before launch and
stop at that cap or the planned session limit.

Count complete trajectories as independent units. Report paired outcomes
by history and model, plus failures by type. Treat the small sample as
descriptive. If both note conditions tie, report the tie and its limits.

## 4. Publish the results and decide on spec changes

Publish the frozen protocol, replay instructions, sanitized results, costs,
and scorer limitations. Release the scored fixtures after evaluation and
reserve fresh cases for the next round.

Advance an OAK convention change only if it addresses an observed failure
and a fresh comparison shows fewer consequential errors in both model
families, with no new errors in approval handling. A tie or a split
across models warrants more evidence before a spec change. Add concurrent
handoffs after the serial cases establish where decisions are lost.
