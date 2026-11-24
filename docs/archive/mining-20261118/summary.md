# Mining agent-memory failures from ohya transcripts

Date: 2026-11-18. Database: `~/.ohya/hub.db` (17 GB), opened
read-only. Outputs: `cases.jsonl` (12 cases), this summary, plus the working
files `candidates.jsonl`, `candidates_kept.jsonl`, `verdicts.jsonl`,
`auto_not.jsonl`, `to_read.jsonl`, `mine.log`, `screen/batch_*.jsonl`.

## Method

### Stage 1 — FTS candidate mining (`mine_candidates.py`)

- Queried the FTS5 index `events_fts` (`rowid = events.id`) with two phrase
  lists: 202 user-correction phrases (for example "we already did",
  "i never said", "you forgot", "outdated", "stale", "we decided",
  "scratch the", "check the log") and 47 agent-discovery phrases (for
  example "log.md is stale", "memory says", "agents.md is outdated",
  "the note is wrong"). Per-phrase hit counts: `mine.log`.
- Kept only `role='user'` events that look human-written: under 1500
  characters, not starting with `<`, `#`, or `[`, and free of injected-context
  markers (`system-reminder`, `<environment_context>`, and similar).
- Raw result: 2454 candidates (claude-code 1864, codex 590).

### Human-turn refilter (metadata-based)

Claude Code delivers tool results as `role='user'` messages, and codex
transcripts carry many non-human payloads, so 1503 of 2454 raw candidates
were not human turns. Refilter by event metadata:

- Drop any event whose message blocks include `type: tool_result`.
- Drop sidechain (subagent) events.
- For codex, require `payloadType = message` and content types limited to
  `input_text`.

Result: 862 candidates (571 user-correction, 291 agent-discovery;
747 sessions, 53 repos).

### Stage 2 — context bundles and screening (`build_context.py`)

- Scored candidates by strong/medium phrase matches, deduplicated by
  normalized text per session, capped the user pool at 3 per session and the
  agent pool at its top 140. Picked 700 of 862 for screening.
- For each pick, fetched the 6 preceding and 1 following assistant events
  (truncated) into 35 screening bundles (`screen/batch_00..34.jsonl`).

### Screening

Every one of the 700 picked candidates received exactly one verdict
(coverage verified programmatically; no overlaps, no gaps):

- 434 auto-classified not-memory by documented noise rules: text starting
  with `You are running in a deterministic RALF loop` (injected loop-task
  templates in the codex pool). Rules for `Continuation guidance:`,
  `You are Worker N`, eval prompts, and pasted compiler/CI output are also
  implemented; their hits were caught during manual reads
  (`auto_not.jsonl`, `verdicts.jsonl`).
- 266 manually read and classified (100 from batch bundles, 166 from the
  ranked `to_read.jsonl` list).

Classification used one category, one source, one preventing fact, and a
confidence level. The same incident is counted once: duplicates marked
`not` with reasons (AX-019 schema saga kept as 58598; dioclet board kept
as 1674040). The two `analyze_image` cases (34973, 45160) stem from one
stale memory note but failed on different surfaces (URL rejected versus
tool absent), so both are kept and cross-referenced.

## Results

12 real memory/knowledge failures out of 700 screened (1.7 percent).

By category:

| Category | Count |
|---|---|
| lost-decision-or-rationale | 5 |
| stale-current-state | 4 |
| repeated-completed-work | 2 |
| conflicting-sources | 1 |

By source of the bad belief:

| Source | Count |
|---|---|
| chat-context | 4 |
| written-note: memory file | 3 |
| written-note: NOTES.md repair records | 1 |
| written-note: to-do/backlog | 1 |
| written-note: project notes/records | 1 |
| written-note: approved scope/plan | 1 |
| code-or-git | 1 |

By preventing fact:

| Preventing fact | Count |
|---|---|
| verification date | 4 |
| status/superseded-by | 3 |
| origin/actor | 2 |
| none | 2 |
| revocation | 1 |

By confidence: 7 high, 5 medium. By agent: 6 claude-code, 6 codex.

## The clearest cases (all 12)

- **58598** (2026-11-08, looper self-run) — An AX-019 schema fix was
  recorded only in a gitignored NOTES.md inside one worktree, so later
  sessions re-diagnosed and re-fixed the same drift across multiple repair
  rounds. repeated-completed-work; written note (NOTES.md repair records);
  missing verification date.
- **1726779** (2026-11-11) — Project notes said two verified copies of a
  dataset existed, but the user had deleted the originals to free disk
  space; the note had no revocation record. stale-current-state; written
  note (project notes/records); missing revocation.
- **2582907** (2026-09-26, decision-model-benchmark) — An agent built the
  benchmark pilot without jev even though the approved scope named jev as
  the main reason for the benchmark; the user had to restate it.
  lost-decision-or-rationale; written note (approved scope/plan); missing
  origin/actor.
- **2539791** (2026-09-15) — The user asked to simplify an existing
  animation; the agent rebuilt it from scratch and discarded the loved
  original. lost-decision-or-rationale; chat-context; no preventing fact
  identified.
- **1548900** (2026-10-06, ncl) — A 30-minute result gave a wrong answer
  for an overnight multi-study ProgramMD run; the agent had stopped after
  one study without recording who owned the run plan.
  lost-decision-or-rationale; chat-context; missing origin/actor.
- **1674040** (2026-11-08, dioclet) — A second agent session redesigned
  the board (8 blocks, extra streets) that another session and the user
  had already aligned on cardo/decumanus orientation.
  lost-decision-or-rationale; chat-context; missing status/superseded-by.
- **211418** (2026-11-07, skillctl self-run) — Two persistent memory files
  still said T048 owned the plans/ docs after T133 executed that scope;
  the agent itself found and updated them. stale-current-state; written
  note (memory file); missing status/superseded-by.
- **119173** (2026-11-05, looper self-run) — A backlog task claimed output
  was unsanitized per review evidence pinned to commit 9850bc2, but git
  history showed the sanitize call predates that review; the agent had to
  rediscover the real defect locations. conflicting-sources; written note
  (to-do/backlog); no single preventing fact (the note already carried a
  commit pin and was still wrong).
- **34973** (2026-11-07, hatch) — The memory-note image workflow (Read
  returns a URL; feed it to analyze_image) no longer worked; the service
  rejected the URL. stale-current-state; written note (memory file);
  missing verification date.
- **45160** (2026-11-07) — Same memory note, different session: the
  analyze_image tool itself was absent from the tool list.
  stale-current-state; written note (memory file); missing verification
  date.
- **645174** (2026-02-25, browser-agent-bench) — The agent forgot the
  earlier decision to attach the last agent message per run as an annex;
  the user corrected it. lost-decision-or-rationale; chat-context;
  missing verification date.
- **1629868** (2026-10-29, agentlab) — A warrant-fix list included one
  issue already fixed and one with a local repro mismatch.
  repeated-completed-work; code-or-git; missing status/superseded-by.

## Honest limits

- **Search bias.** The phrase lists are English-only and correction-shaped.
  A human who corrects without a mined marker ("no, the other file",
  "try again") is invisible to this method, so false negatives are likely
  and the 1.7 percent rate is a lower bound for the screened pool.
- **Pool composition.** The codex pool is dominated by injected templates
  (RALF loop tasks, continuation guidance, worker prompts) and pasted
  terminal output; after filtering, the surviving human-turn pool is
  small. The claude-code pool is dominated by the looper/skillctl
  self-run ecosystem, where agents routinely read memory files. That
  skews the source distribution toward written notes for agent-discovery
  cases and chat-context for user-correction cases.
- **Over-matching on "memory says".** Most of the 291 agent-discovery
  candidates are routine correct memory use ("memory says run focused
  race first"), not discoveries of stale notes. Only 4 of 12 real cases
  come from the agent-discovery pool.
- **Coverage of the kept pool.** 700 of 862 kept candidates were screened;
  the 162 unscreened were lower-scored duplicates inside sessions already
  covered, so additional distinct incidents in them are possible but
  unlikely.
- **Single reviewer.** One reviewer classified all cases from 3-8 events
  of context, not full sessions. Medium-confidence cases in particular
  could resolve differently with fuller context.
- **Incident dedup undercounts recurrence.** The analyze_image note failed
  in at least 3 sessions (34973, 45160, plus duplicates marked not); the
  AX-019 drift recurred across at least 4 sessions. Counts by case, not
  by occurrence.
- **Missing categories.** No wrong-attribution, event-vs-check-date, or
  memory-as-instruction case survived screening. This reflects the phrase
  list and pool, not evidence that these failures do not occur.
- **Redaction.** Quotes were checked for tokens, keys, and signed URLs;
  one quote was trimmed for profanity. Quotes are kept to the minimum
  needed to classify.
