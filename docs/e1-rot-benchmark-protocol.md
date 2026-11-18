# E1 rot benchmark protocol

Status: draft, 2026-11-18. Freeze this file and hash it before the pilot.
Plan: [next phase](next-phase-plan.md).

## Question

Do notes about the current state help or hurt a fresh agent on real
repositories? Does a `check` pointer reduce actions based on stale notes?
Does the encoding of that pointer, YAML or prose, matter?

## Material

Snapshots of papercut (`bb6b252`), looper (`07fa9be`), and barista
(`09065db` plus its working tree) as of 2026-11-18. Each snapshot includes
`.git`. For looper and barista, it also includes the Claude agent memory,
copied to `.agent-memory/`. The answer key is the verified
[memory audit](/notes/2026-11-18-oak-real-memory-failures.md),
`~/oak-experiments/audit-20261118/defects.jsonl`.

## Tasks

Choose 12 tasks, four for each repository where the audit supports it.
Each task must meet all these criteria:

1. It targets one verified defect in a written note.
2. Its true answer can be determined inside the guest from the code, the
   files, or git. Exclude defects about host processes or installed
   binaries unless the repository itself records the truth.
3. The prompt is an ordinary user request. It does not mention notes,
   staleness, or checking.
4. Following the stale note gives an answer or action that differs from
   the truth in a way the scorer can detect.
5. The agent writes `answer.json` at the project root with task-specific
   fields. The scorer may also inspect file edits.

Include at least two tasks whose defect is in a file that all conditions keep
(for example `README.md`, `CLAUDE.md`, or `to-do.json`). These are controls.

## Conditions

Each condition has a `KNOWLEDGE.md` file at the project root that lists the
note files. Every prompt contains the same sentence: "Project knowledge is
listed in KNOWLEDGE.md."

| Condition | Note files | Extra content |
|---|---|---|
| `asis` | Unchanged | None |
| `nonotes` | Removed. `KNOWLEDGE.md` lists none | None |
| `oak` | Claim text unchanged | Each current-state claim gets `as_of` and `check` in YAML |
| `prose` | Claim text unchanged | The same date and check as a sentence |

Note files form a fixed list for each repository, for example `NOTES.md`,
`.agent-memory/`, `knowledge/`, and `LOG.md`. Product documentation,
instruction files, and `to-do.json` stay in all conditions.

In `oak` and `prose`, `KNOWLEDGE.md` adds one identical rule: "Claims about
the current state carry a check. Run the check before you act on the claim."

Annotation rules:

- Do not change, fix, or remove any claim.
- `as_of` is the date when the claim's line was last written: git blame for
  tracked files, the memory file's `modified` field for agent memory.
- `check` is a command or a file that verifies the claim and works inside
  the guest.
- A diff check confirms that only annotations were added.

## Runs

Use Pi 1.5.2 with GLM 5.3 at low thinking and Gondolin 0.14.0 with no guest
HTTP access, through the `pi-gondolin-experiments` runner. Each trial is one
fresh session on a fresh copy of the snapshot.

- Pilot: 12 tasks × 4 conditions × 1 repetition = 48 trials.
- Main run: 12 tasks × 4 conditions × 3 repetitions = 144 trials, if the pilot
  shows that the tasks are not at the score ceiling or floor.
- Run the trials in a seeded random order, with at most two concurrent trials.

## Measures

- Primary: the stale-action rate. This is the share of trials whose answer
  or edit matches the stale note instead of the truth.
- Correct rate. A trial is correct if it matches the truth.
- Check rate. A trial passes if its event log shows a command or read that
  verifies the targeted claim.
- Tool calls and elapsed time.

The scorer labels each trial `correct`, `stale`, or `other`. Review the
`other` trials manually, without condition labels.

## Decision rules

The task is the unit. Compare conditions in pairs across the 12 tasks.

- If `nonotes` has a stale-action rate at or below `asis` and a correct rate
  at or above `asis`, then notes about derivable current state do not help.
  v0.4 then recommends pointers instead of copied state.
- If `oak` or `prose` reduces the stale-action rate against `asis` by at
  least 20 percentage points in the main run, then the check pointer is
  promising.
- If `oak` and `prose` differ by less than 10 percentage points, then the
  YAML encoding becomes optional in v0.4.
- Report the pilot descriptively. Claim nothing beyond these 12 tasks and
  three repositories.

## Threats

- A person who knows the truth chose the check commands. A real note
  writer might choose worse ones.
- The audit verified the defects on one day. The snapshots freeze that day.
- One model. Repeat with GLM 5.3 Flash as a second group if time allows.

## Amendment 1, 2026-11-18, before the pilot

The v1 build showed that most tasks were lookups that named their source,
and that every task had a wrong note. The v2 task set replaces it:

- 12 tasks: 6 stale-note tasks, 4 note-needed tasks where the note is
  correct and is the only source of the truth, and 2 controls.
- Prompts ask for actions or decisions. They do not name the file that holds
  the truth.
- The guest image adds git and jq to the default Alpine image.
- `check_ran` is specific to the claim. The v1 flag remains as
  `check_ran_loose`.
- The task `b5-visual-check` runs, but the primary analysis excludes it. Its
  truth depends on a Claude Code tool behavior that the Pi agent can test
  directly, and the ohya mining found the underlying note unreliable.
- For note-needed tasks, the decision rule for `nonotes` also requires a
  lower correct rate than `asis` before the result can count against notes.

Build details: `~/oak-experiments/e1-rot-20261118/v2/BUILD-REPORT.md`.
