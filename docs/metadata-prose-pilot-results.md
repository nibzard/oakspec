# OAK metadata and prose pilot

Date: 2026-11-18. All 24 sessions completed with exit code zero.

| Measure | OAK | Prose |
|---|---|---|
| Correct format after each session | 12/12 | 12/12 |
| Correct task state after each session | 12/12 | 12/12 |
| Correct named approver in requested answers | 6/6 | 6/6 |
| Total tool calls | 48 | 46 |
| Total elapsed seconds across sessions | 206.2 | 201.7 |

## Design

Three project histories covered export, database, and logging decisions.
Each had an initial approval, a replacement, an unapproved proposal, a later
approval, task completion, and a return to the original choice. Four fresh
sessions ran for each project and condition. Project files carried state
between sessions. Every session started a fresh Gondolin guest.

Both conditions began with the same decision facts and received identical
maintenance guidance and user prompts. OAK added a front-matter block with
kind, status, verification date, and origin. Prose expressed those meanings
in a sentence. The agents maintained their own notes during the experiment.

The test used host Pi 1.5.2, GLM 5.3, Gondolin 0.14.0, and the extension from
the [smoke test](pi-gondolin-smoke-results.md). Guest web access was blocked.
Pi context discovery, other extensions, MCP servers, and skills were disabled.
Six trajectories ran in a seeded random order, with at most two active at once.
The script saved the protocol before starting the sessions.

Configuration checks compared the actual JSON fields with expected values
after each session. Approver checks used manual review of answers from the
first and third sessions. Final notes in all six trajectories preserved the
approval sequence and task completion.

## Findings and limits

Both conditions handled this simple decision sequence. There is no observed
configuration advantage for OAK here. These three histories share one template
and provide only three paired trajectories. Session results within a trajectory
are dependent. No significance claim follows from this pilot.

Verification dates need a separate check. Agents often used the date of an
approval as the date they verified or applied it, despite running in November.
The export OAK run also reported a verification date of 2026-03-02 in its first
answer without a supplied source for that date. These issues do not affect the
configuration score, which does not measure temporal metadata accuracy.

One prose run briefly swapped file contents and repaired the mistake before
exiting. The final-state score does not capture all intermediate errors.
No human repaired files during the runs.

The runner and dependency setup are under `/tmp/oak-gondolin-smoke/`.
The frozen protocol, project files, per-session note snapshots, event logs,
and `results.json` are under `/tmp/oak-compare/`. Temporary storage can be
cleared. Model responses and wall times can vary on a repeat run.

## Next step

Add a check that distinguishes event dates from verification dates. Use
harder histories with conflicting evidence and varied wording before making
a claim about the value of metadata. The current results support keeping
the experiment small while improving what it measures.
