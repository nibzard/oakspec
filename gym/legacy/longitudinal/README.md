# Realistic handoff histories

These fixtures define a 60-session pilot. Each of three histories has ten
sessions in two conditions. The first run completed on 2026-11-18.
[Results and scoring limits](../../docs/longitudinal-pilot-results.md)

| History | Work | Challenges |
|---|---|---|
| `service.json` | Maintain a working sample exporter | Completed migration, rollback, compression approval, old task list, moved approval |
| `cli.json` | Maintain a working backup plan | Conflicting owner notes, explicit resolution, vendor advice, completed restore check |
| `docs.json` | Maintain a public guide | Unapproved marketing copy, withdrawn approval, moved page, independent support decision |

Both conditions start with the same files, facts, and maintenance guidance.
The maintained note uses either OAK metadata or equivalent prose. This tests
that small representation difference. It does not compare every practice in
the published specification. Dates and named actors are fictional test data.

## Run a session

1. Prepare an empty project for session 1. Save the returned prompt outside
   the project. For example, run
   `python3 prepare.py service oak /tmp/service-oak 1 > /tmp/service-oak-prompt.txt`.
2. Run a fresh Pi session with the Gondolin extension, using that project and
   prompt. Keep the configuration fixed across both conditions. Block guest
   web access and use only the experiment's instructions.
3. Save the event log, exit status, elapsed time, and tool calls outside the
   project. Snapshot all project files before applying the next event.
4. Score the snapshot with
   `python3 score.py service /tmp/service-oak 1`.
5. Repeat with session numbers 2 through 10 using the same project. Each
   session needs a fresh Pi process and guest. Use separate projects for
   the other condition and each history.

Keep these JSON fixtures and scoring files outside the guest mount. They
contain answer keys. The preparation command applies external changes before
printing the next prompt. Apply each session once to its intended predecessor.
A retry starts from the saved predecessor snapshot. It must not silently
reinitialize a trajectory or reuse failed partial work.

## Review before the run

Check factual equivalence between conditions and freeze the fixtures, prompts,
scorer, model, and extension versions. Randomize trajectory order with a saved
seed. Use at most two active trajectories initially, as in the earlier pilot.

Automated checks cover configuration fields, required publication markers,
open work, conflicts, approval attribution, and both date meanings. Score a
failed or timed-out session explicitly. Keep that failure in the results.

Also review the exported sample, backup plan output, and complete public text.
Publication markers alone cannot establish that reader-facing wording is
correct. Inspect all note snapshots for lost history, stale statements,
broken references, reopened completed work, and extra invented approvals.
Use event logs to distinguish repeated completed work from a harmless status
check. Label these manual findings separately from automated checks.

Analyze complete trajectories as the independent units. Thirty questions per
condition share three histories. Report descriptive pilot results and use
observed difficulty to decide whether broader tests are justified.

The `run.py` runner automates preparation, fresh Pi processes, event capture,
project snapshots, and frozen scoring. Run `python3 run.py --help` for its
dependency paths. It uses the local agent UID and KVM group launcher tested
on this machine. The protocol and input hashes are saved before any run.
