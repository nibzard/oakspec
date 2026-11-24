# learnings: v0.4 rules without annotations (rules-only condition)

## 2026-11-19 (run day)

- Question: does the v0.4 reading-rule text work without the scoped
  annotations? Third condition `rulesonly` = the replicate's asis tree
  (no `where: dev host` annotations anywhere) with the KNOWLEDGE.md rule
  text byte-copied from the replicate's v04 KNOWLEDGE.md (lead sentence
  + R4-R6). asis and v04 are byte copies of the replicate's trees.
- tasks.json / evaluate.py / test_evaluate.py / launch.py byte-copied
  from the replicate; sha256 90a67b16..., dd455e3a..., 076cf097...,
  a523b170... all match the replicate's own freeze record.
  test_evaluate.py passes 51/51 here.
- External inputs unchanged since the replicate's freeze: run_trial.py
  b5cb3c7e..., guest-image manifest 3a646cd7... (verified before build).
  The draft (f7b63aae...) is no longer a build input; the rule text
  comes from the replicate's v04 tree itself. Recorded as provenance.
- diffcheck-result.json proves: asis and v04 byte-identical to the
  replicate's trees; rulesonly differs from asis in KNOWLEDGE.md only
  (no other file differs, none missing, none extra); the rulesonly
  KNOWLEDGE.md is exactly the asis body + the v04 rule tail, and the
  rule tail equals v04's byte-for-byte.
- Condition name in stems/tables is `rulesonly` (filesystem-safe, no
  second hyphen); the brief calls it "rules-only".
- Smoke (2 trials, before freeze, replicate flow): eb2-gdtools-rulesonly
  valid correct 19.6 s; eb4-zcode-asis invalid_candidate false-verify
  11.7 s — the known asis eb4 behavior, so the pipeline and the new
  condition both work.
- Freeze written before the batch: 6,666 sha256 lines (11 top files,
  conditions trees, 18 trial configs, 5 external provenance lines).
- Batch: 90 trials, seed 20261121, one shuffle, concurrency 2, launched
  2026-11-18 UTC ~21:31 (batch.log, pid in .batch.pid).

## Results (2026-11-18 UTC 21:31..21:51)

- 90/90 trials produced results, 0 errors; 70 valid, 20
  invalid_candidate; no timeouts or agent failures.
- Correct: asis 15/30, rulesonly 27/30, v04 28/30. value-correct
  (status ignored): 27, 29, 29. eb5 0.11.0-from-later-record: 0, 0, 0
  (no trial answered 0.11.0).
- eb4-zcode: 0/5 under asis, 5/5 under rulesonly and v04 — the rule
  text alone flips it, same as with annotations.
- eb5: asis 3 invented (2 x 0.9.1-dev.12 from NOTES.md:129, 1 x
  "0.10.0 (commit 1d7a614)"); rulesonly 1 and v04 1 invented, both
  "0.10.0" with a parenthetical commit suffix that fails the
  evaluator's exact string compare (inherited behavior, kept).
- eb7: 3/5 rulesonly, 4/5 v04, 2/5 asis; the false-verifies are stale
  `contradicted` with note values, the inherited judgment call.
- Post-run freeze verification: all 6,671 workspace entries plus the
  5 external provenance hashes unchanged (6,676 sha lines total; count
  with ERE `grep -cE "^[0-9a-f]{64}  "`, BRE `\{64\}` undercounts).
