# OAK-Bench development calibration

Riverport is a fictional inventory exporter with a local simulated
destination. The fixture gives each fresh session one prompt. Only the
project state carries forward. The harness resets the simulation settings
and outputs between sessions and preserves the raw snapshots for review.

Run one trajectory with an existing Pi–Gondolin trial template:

```sh
python3 oak-eval/oak-bench/run_smoke.py TEMPLATE_JSON \
  .agents/skills/pi-gondolin-experiments/scripts/run_trial.py NEW_OUTPUT_DIR \
  --condition rules --fixture oak-eval/oak-bench/restored.json
```

The template supplies the host command, explicit model, guest extension,
and timeout. The trajectory runner supplies the prompts and project snapshots.
Keep the fixture, scorer, and logs outside the guest project.

The calibration conditions are `none`, `plain`, `rules`, and `oak`.
The follow-up adds `structured`, which keeps the same reading rules
and gives plain Markdown separate sections for owner decisions and
observed deployment settings.
The Riverport fixtures cover an active withdrawal and a restored
approval. The Maplewood fixture tests authority and scope. The scorer checks the final settings, output files, and action
trace. The exporter records a target before writing its output, so a
later deletion of an output file still leaves evidence. The trace is
inside the guest project. Review Pi events in addition to the trace when
an agent changes the exporter or runs a different command.

The [benchmark plan](../../docs/oak-bench-plan.md) defines how to advance
to replication.

See the [calibration results](../../docs/oak-bench-calibration.md).

## Concurrent handoff

Run one pair of writers, merge the branches on the host, then start a
fresh reader. Choose `shared`, `files`, or `oak` for the layout.

```sh
python3 oak-eval/oak-bench/run_merge.py TEMPLATE_JSON \
  .agents/skills/pi-gondolin-experiments/scripts/run_trial.py NEW_OUTPUT_DIR files
```

The runner saves merge conflicts, final settings, and each Pi transcript.
Review the reader's source and reason for the rejection. The public
setting starts disabled, so its final value alone cannot show that the
reader recovered the decision.

## Delivery failures

Run the header and receipt comparisons for an unmerged worktree and an
overwriting import:

```sh
python3 oak-eval/oak-bench/run_delivery.py TEMPLATE_JSON \
  .agents/skills/pi-gondolin-experiments/scripts/run_trial.py NEW_OUTPUT_DIR
```

Each case saves the sender worktree, delivered copy, receipt, fresh reader
transcript, and score. Checked arms verify a known relative path against
the intended sender version and recover the intended bytes when they
differ. The receipt stays outside the guest.
