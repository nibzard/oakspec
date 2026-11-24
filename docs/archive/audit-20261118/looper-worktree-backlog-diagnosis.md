# Looper backlog revert in barista — diagnosis and fix

Branch `fix/backlog-reimport-revert` in `~/looper-fix-reimport`.
Investigated 2026-11-19. All barista and `~/.looper` access was read-only.

## Verdict in one paragraph

The audit's hypothesis was half right. The controller never re-imported or
re-serialized the live backlog from a stale snapshot, and it never overwrote
a verified edit — no revert happened. What actually happened: each worker
runs in a Git worktree into which Looper itself writes a copy of the backlog
at the project task-file path (`to-do.json`), while result snapshots
deliberately exclude that path. Both T123 passes edited that worktree copy
(the second one believing it was "the controller-managed untracked
to-do.json"), reported done, and had their edits dropped: the candidate
commit contained only `LOG.md`, the worktree (the only place the cleanup
existed) was deleted at acceptance, and the live `to-do.json` — written
exclusively from engine state — never changed. The silent drop of an
accepted deliverable is a real looper defect (fixed here, see "The fix");
the "revert" framing is not.

## Timeline (2026-11-18, local UTC+1; journal times are UTC)

| Local time | Event | Evidence |
|---|---|---|
| 05:54–11:31 | T040, T066, T117–T119 complete; the stale deferrals they satisfy remain | barista git log: `d7b2cf1`, `26a9ec3`, … |
| 12:25 | Milestone review's finding becomes task T123, "Stale looper:deferred tags hold back six V1 tasks" | state.db event 10616; `review-5dab22cb7e667689` |
| 12:29 | T123 pass 1 dispatched (attempt `task-7acfdc95f848203b`) | event 10652 |
| 12:48 | Pass 1 accepted: `270e171` "Complete T123" + merge `b178991` "Integrate T123" — **both touch only LOG.md** | `git show --stat`; receipt `files: ["LOG.md"]` |
| 12:55 | Result applied: T123 done in live to-do.json; the seven stale records untouched | event 10789 |
| 13:16 | Review reports "T123's accepted cleanup never reached the live backlog" | event 10837; `review-8b17b4774edcf720` |
| 13:20 | T123 pass 2 dispatched (attempt `task-5be73e5ea282686d`, base `b178991`) | event 10887 |
| 13:35 | Pass 2 accepted: `98e6bb9` + `9f2c33e` — **again only LOG.md** | `git show --stat`; receipt `files: ["LOG.md"]` |
| 13:42 | Result applied: T123 done a second time; queue 0 todo / 35 blocked | event 10924 |
| 14:01 | Review: "Accepted backlog edits never reach the live queue; nine ready V1 tasks stay blocked and nothing can dispatch"; controller idles | events 10963–10969; `review-99674120c61d0b37` |
| 14:01–14:42 | An **external** hand edits the live `~/barista/to-do.json`, clearing the clusters (no controller writer is journaled in the gap — events 10969→10970 are 41 minutes apart) | state.db: nothing between 13:01:03Z and 13:42:12Z |
| 14:42:12 | Idle-boundary import of that edit: `refresh` event + seed `3acd072` "Refresh project baseline for Looper" on `refs/looper/run-29b706c7c379cf95` | event 10970; `git show 3acd072` (timestamp matches to the second) |
| 14:45 onward | Queue resumes: T046, T069, T082, T087, T041, T111 dispatch and complete through the evening ("some hours later the clusters were cleared again") | events 11011+; git log `5f31eaf`, `3edfae3`, … |

The live T123 record still shows the shape the audit saw: `status: done`
while its tags carry `looper:finding:v1-deferrals-stale-after-t040-t066`
and `looper:finding:accepted-backlog-flips-never-reach-live-queue` — review
findings keyed to T123 recorded evidence on the done task, which is the
designed findings behavior, not a status contradiction in the controller.

## Root cause, by code path

1. **Looper plants the file.** `Repository.Workspace` writes the backlog
   into every worktree at the task-file path — `internal/looper/git.go:307`
   (`writeJSON(filepath.Join(p, r.Excluded[0]), b)`). A worker that lists
   its worktree sees `to-do.json` exactly where the project keeps it.
2. **Snapshots exclude it.** `SnapshotFrom` runs `git rm -r -f --cached` on
   the excluded control files — `internal/looper/git.go:240` — so the
   worker's committed candidate ("Complete T123", built at
   `engine.go:1210`) never contains the edit, and
   `e.Repo.Changes(a.Base, commit)` (`engine.go:1219`) reports
   `files: ["LOG.md"]`.
3. **The result path never looked.** `execute` (`engine.go:1112`) compared
   nothing about the worktree task file after the agent ran, unlike the
   review path, which refuses a backlog edit outright
   (`integration.go:582-590`, "review changed the private backlog"), the
   diagnosis consultation (`integration.go:355`), and the context files
   (`context.go:125-138`, "agent changed required context" — this protects
   `to-do.json.context/<session>/backlog.json` but not the root copy).
4. **The edit is destroyed at acceptance.** `applyResult` (`engine.go:1477`)
   removes the worktrees of a done task (`engine.go:1557`). Both T123 worktrees
   (`task-7acfdc95f848203b`, `task-5be73e5ea282686d`) are absent from
   `runtime/worktrees/` today; the accepted cleanup existed only there.
5. **The live file only mirrors engine state.** `export` (`engine.go:353`)
   marshals `e.State.Backlog` and guards the file against *external* change;
   `applyResult` merges only the reporting task's own summary fields. Edits
   to other tasks' records have no channel from a worktree into the queue.
   The designed channels are follow-ups (findings), review `resume`/
   `complete` transitions (T124, not in the running 0.11.0 build), and
   operator edits of the live file imported at boundaries
   (`run.go:1024`, documented in `docs/recovery.md`).

Both T123 passes believed otherwise because the worktree copy is a
convincing stand-in: tracked in Git by the project (the engine's
serialization sitting as an uncommitted modification), at the exact
project path, with a one-line prompt rule ("Do not edit the backlog",
`agent.go:591`) that does not say the worktree copy is that backlog or what
happens to edits of it. The pass-2 receipt states the worker's model
explicitly: "edits stay uncommitted in the controller-managed untracked
to-do.json, so the controller's backlog round must carry them into the
live queue." No such round exists.

## The fix

Smallest correct change: keep the worker-result path from recording a
completion whose backlog change was dropped, and tell the worker why.

- `internal/looper/engine.go` — `execute` captures the semantic digest of
  the worktree task-file copy before the agent runs (`engine.go:1147`) and
  compares it after the agent and context validation (`engine.go:1186`).
  A changed copy returns `worktreeBacklogEditError` (`engine.go:1239-1250`),
  whose message names the file, states it is a read-only mirror, and routes
  backlog changes to follow-ups.
- `internal/looper/run.go:1072-1080` — `applyFinishedWorker` holds the
  attempt blocked with the typed reason instead of an unknown one; the
  worktree stays retained for repair.
- `internal/looper/block_reason.go:55` — new closed-list code
  `worktree_backlog_edit` (class `failure`, retry `after-change`).
- `internal/looper/agent.go:591` — the worker prompt now says the worktree
  copy of the task file cannot reach the live queue and routes backlog
  changes to follow-ups.
- Docs: `docs/tasks-and-checks.md` (new paragraph), one change-log row in
  `docs/AGENT-CONTRACT-MIGRATION.md`. The external-edit behavior in
  `docs/recovery.md` is untouched — the fix changes only the worker
  worktree path.

Behavior now: the T123 shape holds the attempt blocked with
`worktree_backlog_edit`, journals a bounded worker failure summary whose
cause names the file, retains the worktree, and never lets the edit leak
into the live queue. A worker that leaves the copy untouched completes
exactly as before. An operator (or a post-T124 review transition) resolves
the backlog through the existing channels.

## Test results

- New `internal/looper/worktree_backlog_test.go`: the incident route (a
  stub worker flips a stale deferral in its worktree `to-do.json` and
  reports done — asserted: hold with the typed reason, exactly one failure
  summary naming `to-do.json`, T2 unchanged in the live file, worktree
  retained with the worker's files) and the control route (untouched copy
  completes, no such failure). Both failed on the pre-fix code
  (`T1 not held …; status "done"` — the false completion), both pass after.
- `go vet ./...`: pass. `gofmt` clean on every changed file.
- Focused suites (`TestBlockReason|TestControlTags|TestApplyResult|
  TestWorker|TestAgent|TestContext|TestPrompt|TestLegacyContract|TestQuota|
  TestEvents`): pass.
- `go test ./... -count=1 -timeout 40m`: pass (looper package 742.6 s;
  contractschema, ui, and cmd all ok).
- `make build` then `python3 scripts/runtime-test.py`: 73 tests pass in
  441 s, exit 0. The installer, package-smoke, and skill scripts of
  `make test` were not rerun; this change touches the engine and documents
  only (the project's convention for engine-only changes).

## Risks

- A worker that legitimately needs the queue changed now gets a held
  result instead of a silent false done; that costs one repair pass and an
  operator action. That is the intended trade: before, the loss was
  invisible until a review noticed a stalled queue.
- The comparison is semantic (`hashJSON` of the decoded backlog), so
  formatting-only edits pass. A worker that edits the copy and restores it
  byte-identically also passes — matching the review path's semantics.
- Resumed attempts judge only their own session's edits (the anchor is
  captured at each `execute`); a stale edit made in an earlier session on
  a reused worktree is not re-detected. The repair feedback names the file
  to restore, and a requeued attempt gets a fresh, clean copy from
  `Workspace`.
- The held task parks until an operator edit, import, or review transition
  requeues it — blocked tasks are never auto-dispatched. For a
  backlog-cleanup task there is no smaller honest outcome; on builds with
  T124 the review's `resume`/`complete` transitions cover exactly this
  reconciliation.

## What I could not prove

- Who wrote the external edit that landed between 14:01 and 14:42 local.
  The journal records no controller-side writer in the gap; the review
  agents ran in worktrees and their backlog hashes verified unchanged; the
  edit matches, word for word, the operator follow-up both T123 passes
  requested ("Carry the T123 candidate to-do.json into the live backlog
  queue", `owner: operator`). Everything points to a human applying it by
  hand, but no log names the editor — `refresh` records only the digest.
- Whether the pass-1 worker also committed anything beyond LOG.md itself.
  `Repo.Commit` snapshots the whole worktree tree (minus control files),
  so an attempted `to-do.json` commit by the worker cannot have existed in
  the candidate; the receipt's `files` list confirms what the diff carried.
- That no other write touched the live file between 13:42 and 14:01 local
  (between the result export and the review). Export's own guard would
  have refused a mid-flight change and journaled a retention error; none
  appears, so the controller saw its own bytes the whole time.
