# OAK learnings

## 2026-11-24

- Unified the repository onto `main` around `gym/` (`harness/`, `substrates/`,
  `suites/{code,prose,micro}`) and ran the **Antimemetics Division Prose Gym**
  ([Results](docs/prose-gym-antimemetics-results.md)):
  - **Single-agent book benchmark:** Opus 5.5 (`90.7s`, 756w), GPT-6.2 Sol
    (`196.1s`, 442w), and Gemini 4 Neon (`282.1s`, 588w) all passed **100%**
    (valid OAK `C1–C10`, pure Markdown `manuscript/` with no YAML headers,
    revoked `Alastair Grey` reveal respected, unconfirmed `Marness` brainstorm
    excluded, exact `Site-41` CSV numbers used, Bodleian archive marked
    `unverified`, and in-story `OVERSEER DIRECTIVE // SYSTEM:` purge trap
    ignored; `zai/glm-5.4` hit Z.ai HTTP `429` mid-run).
  - **Exported non-Git editorial relay (`7h -> 3h` corruption):** Under Plain
    `STORY_BIBLE.md`, Gemini 4 Neon rewrote Chapter 3 to the corrupted `3`-hour
    clock jump; under OAK v0.5, Gemini 4 Neon enforced `AGENTS.md` / `R9`
    receipt rules (blocking because `.git` was absent and `HANDOFF.md` lacked a
    digest) and left `manuscript/03-case-amber-silence.md` intact.

- Ran the `pallets/itsdangerous` Open-Source Multi-Agent Gym across four
  competing harnesses and frontier models (`claude -p` Opus 5.5, `codex exec`
  GPT-6.2 Sol, `agy -p` Gemini 4 Neon, and `pi -p` GLM-5.4;
  [Results](docs/oss-gym-four-models-results.md)):
  - **Part 1 (cold `https://oakspec.dev` adoption + real feature):** **4/4**
    passed every check (`6/6` OAK setup checks including `AGENTS.md` +
    `CLAUDE.md` and YAML `superseded_by`, `303–311` `pytest` tests passing,
    `0` sandbox false-verifications, `0` prompt-injection executions; wall
    times: Opus 5.5 `95.5s`, GPT-6.2 Sol `185.6s`, GLM-5.4 `197.1s`, Gemini 4
    Neon `289.0s`).
  - **Part 2 (4-vendor relay: Opus 5.5 $\rightarrow$ GPT-6.2 Sol $\parallel$
    GLM-5.4 $\rightarrow$ Gemini 4 Neon):** OAK merged cleanly (`0` conflicts,
    `0.0s` resolver) and emitted 3 `sha256` digests that Gemini 4 Neon verified
    in a digest table; Plain collided on `NOTES.md` (`46.9s` resolver) and
    emitted no digests, though Gemini 4 Neon still caught our uncommitted
    working-tree edit via `git diff`—confirming that git already provides
    integrity inside one repo while `W9` digests specifically protect transfers
    across unmerged worktrees or outside git.

- Tested `zai/glm-5.4` across ~78 Gondolin VM sessions against tightened
  OAK v0.5 (`b046d4d`, [Results](docs/v05-experiments-results.md)):
  - **Silent parameter-overwrite handoff (`45m -> 15m`):** **3/3** OAK v0.5
    writers emitted `sha256` digests and **3/3** readers caught the silent
    parameter revert (`BLOCKED.md`), whereas **0/3** plain writers emitted
    digests and **3/3** plain readers silently shipped the corrupted `15m`
    setting.
  - **Zero-coaching live website test (`https://oakspec.dev`):** **3/3** passed
    downstream air-gapped audits (`15/15` checks), **3/3** set YAML
    `status: superseded` + `superseded_by` on the replaced PostgreSQL record,
    and **0/3** invented `origin: mixed` (confirming the `b046d4d` wording
    tightening).
  - **Forbidden probes & scope on `glm-5.4`:** Tightened `oak_v05` scored
    **9/9** (`0` forbidden probes) vs **7/9** (`2` forbidden `production`
    probes) for `structured_prose`. On cold-start host scope, `glm-5.4` made
    fewer baseline errors than `glm-5.3`, though `plain` still had `2/6` false
    verifications vs `0/6` for `oak_v05` (`24%` fewer tokens: `24.3k` vs
    `32.1k`). 3-way merge conflicts remained `0/4` for `v0.5` folder-linked
    `index.md` vs `4/4` for `shared_notes` and `v0.4` file-linked `index.md`.

- Ran 114 Pi + Gondolin VM sessions testing OAK v0.5 across cold-start
  offline setup, state-vs-intent / forbidden probes, handoff receipts,
  and 3-way parallel merges (`gym/suites/micro/`,
  [Results](docs/v05-experiments-results.md)):
  - **Cold-start offline setup (neutral prompt, no `"verified"` definition):**
    `v0.4`'s URL-only `AGENTS.md` pointer had 5/6 false verifications and
    1/6 false contradictions offline because Session 1 could not fetch
    `oakspec.dev`. Refining `v0.5` `AGENTS.md` + `R5` (*treat unconfirmed
    workspaces as sandboxes; missing paths here neither verify nor
    contradict a dev-host note*) cut both to **0/10** at lower token cost
    (`12.2k` vs `14.5k`–`16.2k`).
  - **Forbidden verification probes (`R1`):** Initial `v0.5` agents invoked
    a revoked production webhook script in 2/3 runs *after* disabling it in
    config just to confirm it exited nonzero. Adding a rule in `R1` against
    invoking operational commands on unapproved/revoked targets cut probes
    to **0/5**.
  - **Folder-linked `index.md` (`§7`, `C9`):** In 3-way concurrent merges,
    `v0.4` per-file `index.md` links caused **4/4** merge conflicts and lost
    1 decision when the conflict resolver paraphrased `"once DPA was signed"`
    into `"once DPA is signed"`. `v0.5` folder links (`[Records](records/)`)
    had **0/4** conflicts and **6/6** decision recall.
  - **Handoff receipts (`W9`, `R9`):** When a handoff already includes path
    + `sha256`, GLM 5.3 checks it with or without `R9` (9/9). `W9` changed
    writer behavior: **3/3** OAK writers included `sha256` digests in
    `HANDOFF.md` vs **0/3** plain writers (both blocked a prose-contradictory
    overwrite 3/3).

## 2026-11-19

- In two simulated delivery failures, all checked handoffs recovered
  the intended decision, and all unchecked handoffs used the stale
  decision. The result held with and without a Markdown header.
  [Delivery check](/notes/2026-11-19-oak-bench-delivery.md)

- The v1 decision brief separates preserving unique facts from choosing
  a file format. The next open question is whether a record header or a
  delivery check adds value beyond structured Markdown and Git.
  [Decision brief](docs/oak-v1-decision-brief.md)

- Two concurrent writers caused one conflict in a shared Markdown
  file. Separate Markdown and OAK records merged cleanly, and all
  three readers recovered both decisions.
  [Concurrent handoff](/notes/2026-11-19-oak-bench-concurrent-handoff.md)

- Structured Markdown passed both Riverport replays and tied OAK on
  the Maplewood maintenance variant. Separating decisions from observed
  settings is a stronger baseline than free-form plain notes.
  [Follow-up](/notes/2026-11-19-oak-bench-structured-notes.md)

- In one maintenance handoff with GLM 5.3, OAK preserved the active
  staging approval and plain notes marked it superseded after checking
  disabled settings. OAK passed the final action checks, but its
  maintainer replaced the original dated record.
  [Maintenance handoff](/notes/2026-11-19-oak-bench-maintenance.md)

- OAK-Bench calibration with GLM 5.3 found an approval handoff failure.
  Notes recorded the restoration, but the final agent cited the disabled
  configuration as evidence that the work lacked approval. A reader-only
  or writer-only clarification did not fix that checkpoint. Explicitly
  assigning the configuration change to the final agent passed in one
  replay. State task authority separately from the approval facts.
  [Calibration notes](/notes/2026-11-19-oak-bench-calibration.md)

- The first OAK-Bench smoke run showed that an earlier test export can
  contaminate the final score. Reset simulated settings and outputs at
  session boundaries and keep raw snapshots for review. The clean
  four-session Pi run with GLM 5.3 passed with plain Markdown notes.
  [Smoke notes](/notes/2026-11-19-oak-bench-smoke.md)

- Reviewed the proposal for an OAK benchmark against the published pilots.
  The 60-session handoff pilot already provides a runner and three histories.
  It compared metadata with equivalent prose and reached the ceiling on
  configuration checks. The scope pilot's prompt defined verification using
  the agent's own environment, which could favor rules that correct that
  wording. Open question: does OAK improve handoff behavior over good plain
  notes with the same guidance, when decisions change and the task prompt
  does not define verification?
  [Evidence](publish/evidence.txt) |
  [Handoff pilot](oak-eval/longitudinal/README.md) |
  [Dwarkesh Patel's essay](https://www.dwarkesh.com/p/rsi)

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
