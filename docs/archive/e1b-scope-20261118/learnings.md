# E1b learnings

Working log for the E1b check-scope experiment in this directory.
Protocol: ~/oak/docs/e1b-check-scope-protocol.md (frozen, hashed).

## 2026-11-19 build session

- Task selection: 6 environment facts, 3 true (eb1 android paths from E1 b2,
  eb2 gdtools from E1 b3, eb4 zcode) and 3 stale on the host today
  (eb5 installed looper binary 0.10.0 vs host 0.11.0, eb6 node/claude
  versions from LOG row 18, eb7 Godot at /Applications/Godot.app vs host
  ~/.local/bin/godot). All verified on the host; outputs in keys/.
- The looper repo has few usable host facts: the binary version (two
  claims), zcode-missing (buried in a plan fact list), claude Pro auth
  (not cheaply checkable), and timing folklore (not verifiable by one
  command). Barista carries 4 of 6 tasks; documented as an imbalance.
- LOG.md:18 (2026-10-13 "Set up local environment") is a macOS-era row:
  /Applications/Godot.app, /opt/homebrew, "Java is absent". The project
  later moved to the Linux dev box, so the whole row's environment claims
  are stale today. Rich source for stale tasks.
- Conditions built from the E1 v2 trees (copy + annotate), not from the
  raw snapshots: unscoped = E1 oak + new environment claims; scoped adds
  `where: dev host` to every claim whose check is a `host:` check;
  scoped-prose is the E1 prose tree plus the same scope as a sentence.
- Deviation from E1 (documented in build_conditions.py): E1's annotation
  on NOTES.md:30 (installed binary 0.10.0) used `git tag` as the check,
  which verifies the newest tag, not the installed binary. E1b swaps in
  `host: looper --version`. A check that does not check its claim would
  confound the scope manipulation.
- Regex traps while annotating: a `[^.]*` span breaks on checks that
  contain a dot (/Applications/Godot.app); use non-greedy `.*?` up to the
  closing `.)`* of the prose annotation. Count grep hits by match, not by
  line: two annotations on one LOG row share a line.
- E1's oak KNOWLEDGE.md is not exactly asis + rule (it drops a blank line
  before the note-file list); the diffcheck compares KNOWLEDGE.md against
  the exact expected bytes per condition instead of reconstructing it.
- Scoring decision: on stale tasks `contradicted` maps to false-verify
  (unearned determined status) because no E1b stale task has repo
  contrary evidence (the protocol allows contradicted as correct only
  when it does). On true tasks it maps to false-reject. The asymmetric
  mapping is documented in evaluate.py.
- Flash model id confirmed by probe: zai accepts `glm-5.3-flash`
  (probe/flash-model-probe.txt). Flash group reuses the E1 v2 conditions,
  prompts, and evaluator unchanged; only --model differs.

## 2026-11-19 run results

- All 156 trials exited normally (no timeouts, no agent failures).
- Correct: asis 12/30, unscoped 16/30, scoped 18/30, scoped-prose 19/30.
  False-reject only in asis (2). Stale-task correct rises with scope.
- eb4-zcode saturates: 20/20 false-verify in all conditions. The guest
  also lacks zcode, so a guest check agrees with the note and every agent
  says "verified". A coincidentally-consistent check beats every
  annotation.
- 28 of 29 stale false-verify answers said "contradicted" after running a
  guest check that could not apply (eb6's guest node version differs from
  both note and host; one transcript saw v24.22.3, a third value).
- Quotes show the scoped agents citing `where: dev host` verbatim when
  keeping notes unverified; the correct eb5 unscoped quote reasons the same
  way without the annotation.
- Flash group ceiling: 17/18 correct in asis and nonotes; one stale
  (l4-t142 asis r2), one other (p1-release-notes nonotes r3).
- Pitfall for future runs: `run_batch.py ... | tail -30` buffers the live
  log; read the output file of the background task for progress instead.
