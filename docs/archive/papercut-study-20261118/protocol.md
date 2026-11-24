# Study protocol: OAK memory versus no OAK for coding agents in Papercut

Frozen on 2026-11-18 before any confirmatory worker run. Hashes of the frozen
files are in `PROTOCOL_HASHES.txt`. Pilot data in `/tmp/papercut-oak-comparison`
informed only the choice of worker command and time budget. It did not set the
rubric, which was derived from the current repository sources and audited by
`scripts/audit_rubric.py` (58/58 checks pass, see `results/audit_rubric.log`).

## Research question and estimand

Does an in-repository OAK-0001 knowledge base (the `knowledge/` directory plus
its pointer lines and frontmatter metadata, present as uncommitted changes in
`~/papercut`) improve how well a coding agent answers questions about
a repository, compared with the same repository without that integration?

The treatment is the working-tree difference alone. Both conditions share the
same Git history at commit `6ca98a4`, the same prompts, model, settings, tool
permissions, output limits, and time budget. The estimand is the mean paired
difference in task accuracy between conditions.

## Conditions

- `oak`: disposable copy of the OAK working tree. Verified byte-identical
  `git diff` and `knowledge/` content against the original checkout.
- `control`: disposable clone at `6ca98a4` with a clean tree. This matches the
  pre-OAK state; the integration is absent.

Each run gets a fresh copy under `runs/<run_id>/repo`, so no run shares a
working directory, project key, or session state with another run.

## Task set

Fifteen fixed tasks: three each for history, freshness, unresolved work,
provenance, and authorization (`tasks.json`). Every task has one correct answer
set for both conditions; the audit proved each rubric element is derivable from
the control tree. Seven tasks are classified `served_by_memory` (the knowledge
index or its frontmatter states the substance); eight are memory-neutral. The
set avoids asking only facts written in the OAK setup record: most elements
come from shared documents, source code, or Git history.

## Hypotheses

- H1 (primary): with OAK, task accuracy is higher than without.
- H2 (secondary, directional not claimed): OAK changes efficiency metrics
  (turns, tool calls, output tokens, wall time) and per-subset accuracy.
- H0: no accuracy difference.

## Endpoints

- Primary: per-run accuracy score on the frozen rubric, 0 to 1
  (earned element points divided by element count for the task).
- Secondary: model turns, tool calls, output tokens, wall seconds, plus
  accuracy per category, for the memory-served subset, and for the
  memory-neutral subset.
- Token accounting: input-token counts are reported but not compared as a
  primary metric, because context composition can differ; cache-read and
  cache-creation tokens are reported separately.

## Sample size and power

Design: 15 tasks x 2 conditions x 4 repetitions = 120 runs (the upper end of
the study budget). The minimum difference that matters is 0.15 accuracy points
(15 points on a 100-point scale). Below that, the upkeep cost of a knowledge
base is not justified. Simulation (`scripts/power.py`, `results/power.json`):
task-mean paired differences have standard deviation `sqrt(2*sigma_w^2/4)`
for run-level score deviation `sigma_w`. Power for the exact sign-flip test:

| Run-level sigma_w | 0.15 | 0.20 | 0.25 | 0.30 |
|---|---|---|---|---|
| Power at delta=0.15 | 1.00 | 0.97 | 0.86 | 0.74 |
| Power at delta=0.10 | 0.92 | 0.70 | 0.54 | 0.40 |

Simulated type I error at delta=0 is 0.044 to 0.050. The study is powered for
the target effect when `sigma_w` is at most about 0.25. A null result is
reportable regardless.

## Randomization and blinding

- Run order is a uniform shuffle of all 120 runs, seed 20261117, written to
  `runs/manifest.json` before execution.
- Concurrency is capped at four workers; the pool draws runs in shuffled order,
  so conditions interleave across time.
- Scoring is a deterministic script (`scripts/grader.py`) that reads run
  answers and the rubric only. It is blind to condition by construction.
  Condition labels are joined only in `scripts/analyze.py`.

## Worker specification

Identical for both conditions: `claude-zai -p` (fresh session per run), model
from the shared claude-zai settings (`glm-5.3`), `--restricted` with tools
`Read,Glob,Grep,Bash`; Bash allowlist limited to read-only Git subcommands;
`--strict-mcp-config` with an empty MCP config (no MCP servers in either
condition); `--no-session-persistence`; `--permission-mode dontAsk`;
stream-JSON output; wall-clock timeout 900 seconds. The full command line is
recorded in each `meta.json`.

## Isolation and residual confounds

Removed by design: MCP servers (including the ohya session hub and axinbox);
cross-session context (fresh `-p` sessions, unique working directory per run);
cross-checkout access (`--restricted` confines file tools to the run's working
directory); writes (tool allowlist; post-run `git status` checked for
modifications); network (no allowed tool reaches the network).

Residual confounds, recorded not removed:

- The oak tree contains uncommitted changes; a worker that runs `git status`
  sees a dirty tree. This is part of the tested integration, but it differs
  from control.
- The oak tree's instruction files point to `knowledge/`; this pointer is the
  treatment mechanism, not a confound.
- Worker transcripts of this study could in principle enter the ohya hub, but
  no worker can reach the hub (no MCP) and each run uses a unique project
  path.
- The coordinator session ran with the ohya MCP denied, so no rubric content
  can reach any worker through memory.
- Both conditions load the same global user instructions.
- Model or provider drift over time is shared by both conditions through
  interleaving.

## Exclusion rules and intention to treat

All 120 randomized runs are analyzed. A run that times out or errors keeps its
observed output; a run with no answer text scores 0 on accuracy. Efficiency
metrics are missing for failed runs and reported as missing counts. No result
inspection before analysis. The only permitted exclusions are duplicate
executions of the same run id or runs whose tree failed verification before
any worker start; none are expected, and any would be logged here.

## Analysis plan

- Aggregate to task means per condition; paired differences (oak minus
  control), 15 pairs.
- Primary test: exact two-sided Wilcoxon signed-rank, alpha 0.05, zeros
  dropped and reported. Companion tests, pre-specified: exact sign-flip
  permutation on the mean, and paired t interval.
- Effect sizes: mean paired difference with bootstrap 95% interval
  (10,000 resamples, seed 987654321), standardized dz, and the
  Hodges-Lehmann estimate.
- Secondary family: turns, tool calls, output tokens, wall seconds, five
  category scores, two subset scores. Holm correction across the secondary
  family; raw and adjusted p values reported.
- Failures and missing data reported per condition.

## Reproduction

```
cd /tmp/papercut-oak-study
python3 scripts/audit_rubric.py
python3 scripts/power.py
python3 scripts/runner.py build
python3 scripts/runner.py run
python3 scripts/grader.py
python3 scripts/analyze.py
```

Raw data: `runs/<run_id>/{stream.jsonl,stderr.txt,meta.json,extracted.json}`;
scores in `results/`; analysis in `results/analysis.json`; report in
`report.md`.
