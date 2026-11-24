# Project memory audit — papercut, looper, barista

Audit date: 2026-11-18. Read-only analysis. Every defect in `defects.jsonl`
was verified against code, git, or live process state on this machine.
Scope: in-repo notes, agent memory directories, git log and git notes, and
looper runtime state.

Looper manages barista (runtime dirs `~/.looper/barista-bdbd24f2` and
`~/.looper/barista-bbdbd24f2`; a looper daemon, PID 716685, owns it), so
barista is in scope.

## How each project stores knowledge

### papercut

- In-repo documents: `PLAN.md` (spec), `README.md`, `RELEASES.md`,
  `docs/USAGE.md`, `docs/triage.md`, `docs/releases/*.md`,
  `plans/review-2026-08-06.md`, `plans/implementation-review.md`.
- OAK-0001 knowledge store added 2026-11-18 (commit `bb6b252`):
  `knowledge/index.md` plus per-file `oak:` frontmatter (kind, at, status,
  superseded_by) on seven historical notes. Operational docs were left
  without metadata on purpose.
- Agent memory: `~/.claude/projects/-home-agent-papercut/memory/`
  is empty. All memory is in-repo.
- Git: no notes. Five tags, `v0.1.0` through `v0.2.3`.

### looper

- `NOTES.md` (1,176 lines): the working memory. A "Current state" section at
  the top, then dated sections, then an archive index after a 2026-11-13
  compression (9,829 lines cut to `/notes/NOTES.md.full-2026-11-13.md`).
- `to-do.json` (146 tasks) with `to-do.schema.json`.
- `docs/` plans, each with a `Status:` line; release notes per version.
- Agent memory: 124 files under
  `~/.claude/projects/-home-agent-looper/memory/` with a `MEMORY.md`
  index. Files carry Claude auto-memory frontmatter (`modified`,
  `originSessionId`) — an origin and a date, but no checked, status, or
  supersede fields.
- Git notes on `refs/notes/context` (10 notes). Task work under
  `refs/looper-tasks/*` and run refs `refs/looper/run-*`.
- Runtime state in `~/.looper/looper-f42bdd84/` (controller.json and
  friends) holds the live truth the notes describe.
- No OAK metadata anywhere.

### barista

- `LOG.md` (239 KB): one table, one row per completed task, written by the
  looper-run agent. Rows self-date. No machine attribution.
- `to-do.json` (124 tasks, no creation dates) with a schema that the live
  file violates in 38 records.
- Design docs: `GAME_DESIGN.md`, `ART_DIRECTION.md`, `brainstorm.md`,
  `CLAUDE.md`, `README.md`.
- Agent memory: 25 files under
  `~/.claude/projects/-home-agent-barista/memory/`, same
  auto-memory frontmatter as looper, plus a `MEMORY.md` index that matches
  the file set.
- Git notes (3) consistent with their LOG rows.
- No OAK metadata anywhere.

## Defect counts

46 verified defects total: papercut 5, looper 20, barista 21.

| Category | papercut | looper | barista | total |
|---|---|---|---|---|
| 1 stale current state | 2 | 6 | 7 | 15 |
| 2 done/open confusion | 0 | 2 | 2 | 4 |
| 3 conflicts | 1 | 2 | 6 | 9 |
| 4 missing/wrong dates | 2 | 0 | 2 | 4 |
| 5 missing origin | 0 | 0 | 1 | 1 |
| 6 superseded, no pointer | 0 | 3 | 1 | 4 |
| 7 broken references | 0 | 6 | 1 | 7 |
| 8 agent instructions in notes | 0 | 1 | 1 | 2 |

## The 15 most important verified defects

1. **barista to-do.json:1427,1615,2238 — three tasks blocked on done T040.**
   The T123 pass cleared these deferrals on 2026-11-18 (LOG.md rows 114-115)
   and the live file has them back: blockers still say "T040 lands the
   section 18 auto-save system" while T040 is done (05:01Z). A controller
   re-import reverted verified queue edits.

2. **barista LOG.md:115 vs live to-do.json — asserted queue state does not
   exist.** The row claims "10 todo, 26 blocked, 88 done" after the edit.
   Live: 0 todo, 35 blocked, 89 done. T123 is done (12:42Z) while its own
   details say its "accepted cleanup never reached the live backlog".

3. **barista to-do.json:2504-3141 — four tasks blocked on done T066.** Same
   revert cluster; the brewed-payload prerequisite landed (commit 26a9ec3)
   and the blockers quote it as future work.

4. **looper memory looper-t142-quota-reset-cue-parsing.md:11 — task recorded
   as fixed, backlog says blocked, code has no trace.** T142 is `blocked` in
   to-do.json; the named symbols do not exist in `internal/`; the "Complete
   T142" commit sits only on a task ref, never integrated. Memory written at
   completion time in a worktree the main tree never received.

5. **looper NOTES.md:19 — "No controller runs."** A detached controller (PID
   968618, session `run-2be06429adcf2813`, started 2026-11-17T23:02Z) owns
   the repository while the notes' authoritative header says otherwise.

6. **papercut docs/triage.md:56 vs :97 — "The current CLI has no `close`
   command" in the same file that instructs `papercut close`.** The command
   has existed since 2026-09-19 (`d6a6841`); the sentence was stale the day
   it was written (2026-09-29) and still stands.

7. **looper NOTES.md:30 — installed binary recorded as 0.10.0.** Installed
   binary is 0.11.0 (`f86cf80`); the same notes record preparing the 0.11.0
   release notes but the header was never refreshed.

8. **barista to-do.json:2232/2245 and 2445/2463 — shipped work still
   blocked, self-flagged.** T069 and T079 carry finding tags
   (`...outcomes-shipped-status-stale`, `city-hud-flip-done`) that say their
   outcomes shipped (city_run.gd:885, :128); both remain `blocked`.

9. **papercut PLAN.md:10 — "any release remain[s] separate work."** Five
   releases exist (v0.2.3 published 2026-11-17) and papercut 0.2.3 is
   installed with a live managed block in `~/.agents/AGENTS.md`. The OAK
   spec frontmatter carries no `as_of`; the setup journal explicitly chose
   not to date claims it had not reverified.

10. **barista to-do.json:1374/1413 — done T040 carries evidence text its own
    acceptance contradicts.** Details still say the save system "exposes only
    record_tower_switch"; `record_save_point` exists and records three save
    points. LOG.md:114 says the finding tag was removed; it is still present.

11. **looper docs/OPERATOR-WORKFLOWS-PLAN.md:5 — "Status: implementation
    proposal" after implementation shipped in 0.11.0.** Sibling plans got
    "Status: implemented" updates; this one was missed (NOTES.md:413
    records the implementation).

12. **barista to-do.json — 31 blocked tasks undated, 0 of 146 have
    created_at.** The schema defines both fields. A reader cannot tell when
    a "Deferred: ..." condition was last evaluated, which is what lets
    defects 1-3 survive.

13. **looper memory looper-ax-selfrun-complete.md:15,29 — dead
    instructions.** "The controller sits in Waiting" (it was stopped
    2026-11-13) and "merge /notes/NOTES.md.pre-restore ... into NOTES.md"
    (superseded by the 2026-11-13 compression). A session obeying it would
    re-merge ~9,800 deleted lines.

14. **barista LOG.md:26 vs :77 vs memory — three-way gdtoolkit provenance
    conflict.** "No installs needed" (10-13) vs "Installed ... with pipx"
    (11-15) vs memory: pip user-site install, "this box has no pipx"
    (11-18). CLAUDE.md:16 and README.md:24 still teach `pipx install`, a
    command that cannot work on this machine.

15. **papercut knowledge store born stale.** `knowledge/index.md`
    (`as_of: 2026-11-17`) lists release history ending at v0.2.1. v0.2.2 and
    v0.2.3 shipped the evening of 2026-11-17, before the store's commit
    (2026-11-18 08:47). The metadata asserted a currency it never checked.

## Judgment

The dominant failure is **maintenance, not representation**. About two
thirds of the defects (all of categories 1, 2, 6 and most of 7) are content
that was true when written and that nobody re-checked after a later event:
a release, a landing, a controller start, a ref rebuild, a scope decision.
Three mechanisms produce them:

- **State duplicated across layers that update independently.** Looper's
  NOTES.md header, to-do.json, memory files, and run refs each describe the
  same state; the controller appends new sections but never refreshes the
  "Current state" block (defects 5, 7, 8).
- **A writer whose work is discarded or never integrated.** Barista's queue
  edits are reverted by controller re-imports (defects 1-3); looper's task
  memory is written inside task worktrees whose commits never reach main
  (defect 4).
- **One-directional bookkeeping.** Records get written at event time but
  no rule forces a revisit when the referenced fact changes (defects 10,
  11, 15 and every stale blocker).

Representation still matters in a specific way: the missing fields are
exactly the ones that would make the staleness *visible*. Categories 4 and
5 (undated records, unattributed machines) and papercut's unfilled OAK
fields (`as_of` omitted on the spec, `at` omitted on records whose dates
were one git command away) show that dates, origins, and check stamps turn
silent rot into checkable rot. Papercut's OAK store also shows the limit:
where the metadata was filled (`superseded_by`, `at` on the August
reviews), it worked; where the setup guessed or skipped, the metadata
itself became a defect. Barista's self-flagging finding tags (defect 8)
prove that even perfect self-documentation changes nothing without an act
that closes the record.

Verdict: assign every current-state claim a checked date and an origin,
but expect no fix from format alone. The failing step is the revisit: some
agent or process must re-verify claims when their referent changes, and a
write path must not be able to silently discard a verified edit.
