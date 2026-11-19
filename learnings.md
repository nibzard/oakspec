# OAK learnings

## 2026-11-19

- Added the project mark, "The Keeping Oak", in `brand/`. One seeded oak
  geometry feeds the 4K artwork, the medallion mark, the favicons, and a
  one-ink print mark. `@napi-rs/canvas` renders it in Node in about 30
  seconds, with no headless browser. Its `ctx.filter = 'blur()'` works.
- Simulated paper tooth shows whatever is under a layer, not the paper. Make
  base fills solid (pressure 1), or the sky speckles through the hills.

- Correction: the barista backlog "revert" was not a revert. A looper worker
  edited the worktree copy of `to-do.json`, which result commits exclude, and
  the edit was lost when the worktree was deleted. A person later applied it
  by hand. Fixed on looper branch `fix/backlog-reimport-revert`. This is the
  write-path loss that v0.4 rule W9 describes.
  [Report](../oak-experiments/looper-fix-REPORT.md)
- OAK-0001 v0.4 is live at https://oakspec.dev with `/evidence.txt` and the
  archived `/oak-0001-v0.3.txt`. Cloudflare took about 30 seconds to serve
  the new `llms.txt`.

- v0.4 candidate checks (51 trials): with the draft's reading rules R4 to R6,
  the E1b scope tasks scored 28 of 30 correct with no false verifications.
  The best E1b condition scored 18 of 30 with 11. This compares two runs. A
  same-batch replication is running. Setup from the draft kept every note
  line in 3 of 3 trials, but one agent's summary claimed edits that the files
  did not contain. Deletion, revocation, and injection cases were at the
  ceiling with and without OAK. Eight spec defects were fixed in the draft.
  [Report](../oak-experiments/v04-checks-20261119/REPORT.md)
- The R4 to R6 result replicated in one batch of 90 trials: `asis` 12 of 30
  correct with 14 false verifications, `scoped` 19 with 11, `v04` 28 with 2.
  Only the rule text differed between `scoped` and `v04`. Short reading rules
  changed behavior more than any metadata did in any test.
  [Results](docs/v04-candidate-results.md)
- The rules work without metadata: plain notes plus R4 to R6 scored 27 of 30,
  against 28 for annotated notes plus the rules and 15 for plain notes alone.
  OAK's value in these tests came from short reading rules, not from fields.
  [Results](docs/v04-candidate-results.md)
- E1b (156 trials): agents often check a claim in their own sandbox and call
  a claim about the dev host verified. This happened in 11 to 14 of 30 trials
  per condition. A `where` scope raised correct answers from 12 to 18 of 30.
  Offering an `unverified` status stopped the false rejection seen in E1.
  YAML and prose tied. GLM 5.3 Flash followed a stale derivable note in only
  1 of 18 trials. [Results](docs/e1b-check-scope-results.md)

## 2026-11-18

- E3 (36 rounds): no note layout lost records through `git merge`. Append-only
  records had a quarter of the conflicts, and their rounds took 52 seconds
  against 230 for the v0.3 index layout. Unmerged branches and overwriting
  imports remain untested. [Results](docs/e3-parallel-writes-results.md)
- E1 pilot (48 trials, real repositories): stale notes about derivable state
  caused no stale actions. Agents verified from code and git. Notes mattered
  only for facts the agent could not check. YAML and prose gave identical
  outcomes. [Results](docs/e1-rot-pilot-results.md)
- Use a process ID, not `pgrep -f` with a phrase, to wait for a background
  worker. The wait loop's own command line matches the phrase, so the loop
  never ends.

- An audit of the papercut, looper, and barista memory found 46 verified
  defects. Most were true when written and went stale after a later event:
  a release, a merged task, or a controller start. Dates did not prevent
  this. The looper header said "Current state, 2026-11-13" and was still
  wrong. Writes also got lost: task memory stayed in unmerged worktrees, and
  a controller re-import reverted verified backlog edits.
  [Notes](/notes/2026-11-18-oak-real-memory-failures.md)
- Mining ohya found only 12 human corrections caused by memory failures in
  700 screened candidates. Most real failures are silent, or agents
  re-derive the current state from code. Lost decisions and stale tool
  workflows caused the visible failures, not missing metadata syntax.
  [Notes](/notes/2026-11-18-oak-real-memory-failures.md)
- Pilot artifacts from `/tmp/` now live in `~/oak-experiments/`, without
  credentials or `node_modules`.

- A project skill now captures the reusable Pi–Gondolin experiment workflow.
  Its runner preserves isolated input copies and logs for valid, invalid,
  timed-out, and failed trials. Tests covered those outcomes and protection
  against reused output directories. Experiment-specific evaluators and
  dependency setup remain explicit.
  [Skill](.agents/skills/pi-gondolin-experiments/SKILL.md)
- The harder 60-session pilot completed. Both conditions kept all checked
  operational settings correct. OAK used 180 tool calls and prose used 192.
  The OAK service note temporarily lost its metadata delimiter. Approval-date
  attribution also differed in the OAK backup trajectory. The raw scorer
  penalized `done` versus `complete` and broadly worded open-task reports.
  Fix these measurement definitions before another comparison.
  [Results](docs/longitudinal-pilot-results.md)
- Three harder histories are ready for a 60-session comparison. They cover
  a service, a backup CLI, and documentation. Preparation and scoring were
  checked for all session/condition combinations, including rejected wrong
  verification dates. The first run is complete. Public wording and lost
  history need manual review alongside automated scores.
  [Fixtures and procedure](oak-eval/longitudinal/README.md)
- The [v0.4 timeline](docs/v0.4-timeline.md) proposes realistic longitudinal
  tests before the specification draft. Two working weeks is a planning
  estimate. Simple configuration checks have reached the score ceiling,
  so the next comparison must measure actions after knowledge changes.
- A 24-session Pi–Gondolin pilot found correct configurations in all 12 OAK
  and all 12 prose sessions. Requested approver answers were also correct.
  OAK used 48 tool calls and prose used 46. These simple cases reached the
  score ceiling. Agents also confused approval dates with verification dates,
  which needs a separate check. [Results](docs/metadata-prose-pilot-results.md)
- The Pi–Gondolin smoke test passed. Host Pi edited the mounted project
  through guest tools. An unrelated host file was inaccessible, and guest
  web access was blocked. A fresh guest retained the project edit but had
  no scratch file from the first guest. The test needed QEMU tools and
  temporary KVM group access. [Results](docs/pi-gondolin-smoke-results.md)
- Start with Pi on the host and Gondolin for its tools. The test needs fresh
  agent state, controlled inputs, and isolated project access. Running all
  of Pi in the guest adds setup work before we know it is needed. Use a
  fresh guest and Pi session for each handoff. Carry only the project
  between sessions in one trajectory. This is the proposed first approach.
- Gondolin supports fresh guests, network policies, and disk checkpoints.
  The initial host check found no QEMU and no KVM access for the default
  process groups. The smoke test resolved both dependencies for its runs.
  [Research notes](/notes/2026-11-18-oak-gondolin.md)

- In the Papercut study, OAK and control had similar accuracy. OAK used
  fewer tool calls on average, but the difference was not statistically
  significant. The study covered one repository and one model.
  [Report](report.md)
- The study combined metadata, an index, and curated notes. It cannot show
  which part caused a difference. Compare OAK with equally informative prose
  to test the value of metadata. [Research](research.md)
- In one handoff pilot, both OAK and plain Markdown carried a decision through
  a fresh agent session and a later change. The OAK setup included a local
  copy of the specification. The plain notes had two broken links.
  [Pilot results](docs/offline-handoff-results.md)
- The pilot used one case per condition. Its guidance differed between
  conditions, and the operating system did not enforce network isolation.
  The pilot does not establish which approach is more reliable.
  [Pilot results](docs/offline-handoff-results.md)
- A fresh agent fetched OAK from the website and saved a local copy. Two
  handoff sessions used no network tools in their logs and tracked the
  decision change. Both wrote uppercase configuration values despite the
  project's lowercase rule. The local spec differed slightly from the
  published text. [Website pilot](docs/website-handoff-results.md)
- The E1 rot benchmark was built and smoke tested
  (`oak-experiments/e1-rot-20261118/`). The Gondolin guest has python3,
  grep, node, and find, but no git, jq, go, make, or cargo; every task
  truth and annotation check must read .git as plain files (loose refs
  and tags) instead of running git. The live repos drifted past the
  audit within hours: barista's T040/T066 blocked-on-done clusters were
  cleared and looper's run-ref tip moved again, so task truths must be
  re-verified inside the frozen snapshot, never copied from the audit.
  [Build report](../oak-experiments/e1-rot-20261118/BUILD-REPORT.md)
- The E3 parallel-writes experiment was built and smoke tested
  (`oak-experiments/e3-writes-20261118/`). Git worktrees break inside a
  Gondolin guest mount: the worktree's `.git` pointer file names a host
  path that does not exist in the guest, so writers get "not a git
  repository" and the orchestrator must commit and merge on the host. A
  full clone (real `.git` directory) inside the mount works fine in the
  guest, which is why the resolver and reader sessions run in the round
  repo, not in worktrees. The smoke (3 rounds) showed the expected
  structure: shared and oak-index conflicted and needed resolvers,
  append merged cleanly, and nothing was lost yet.
  [Build report](../oak-experiments/e3-writes-20261118/BUILD-REPORT.md)

## 2026-11-19: blog review corrections

- Every E1b-family task prompt defines "verified" as "you checked the
  values in your environment". This invites the sandbox false
  verification in every condition. Disclose it whenever the R4 to R6
  result is cited, and use a neutral prompt in the cross-model run.
- The scope result has four batches (E1b, candidate check, replication,
  rules-only), not three. Only replication and rules-only are
  same-batch comparisons.
- zcode 35/35 false verify = E1b 4 conditions (20) + replication 2 (10)
  + rules-only asis (5). Charts show only 2 of the 4 E1b conditions.
