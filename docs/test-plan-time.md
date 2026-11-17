# Test plan: does OAK keep memory correct over time?

Status: draft, 2026-11-17. Spec under test:
[OAK-0001 v0.3](https://oakspec.dev/oak-0001.txt).

## Question

Over many sessions, does memory kept by the OAK-0001 practice stay more
correct than memory kept without it? Is the cost acceptable?

The setup test showed that agents can set up OAK from the text alone. This
test checks the main claim: memory stays current. The mining of real
sessions found that the common failure is drift: status, plans, decisions,
and "next" items stop matching reality
(`/notes/2026-11-17-oak-failure-mining.md`). This test targets drift.

## Hypotheses

- **H1.** With OAK (C), fewer probe answers are wrong or stale in late
  sessions than with the same practice written as prose (B).
- **H2.** With OAK (C), fewer probe answers are wrong or stale than with no
  convention (A).
- **H3.** OAK costs at most 20% more tokens per session than B.

H1 is the decisive comparison. H2 alone cannot separate the effect of the
metadata from the effect of having any written practice.

## Conditions

All conditions use the same agent, model, tools, and session prompts. Only
the memory instructions differ.

| Condition | Memory instructions given to the agent |
|---|---|
| A. No convention | "Keep project memory in `memory/` as you see fit." |
| B. Prose practice | A version of OAK-0001 with the same habits (kinds, setup, Section 9 routine, self-check) but no `oak:` block. Facts such as dates, status, and replacements are written as sentences. |
| C. OAK-0001 | The published text. |

B must have the same length and the same advice as C. Write it by editing
the published text, not from scratch. Review B and C side by side before any
run.

## Design

### Worlds

A world is a scripted project history: 10 to 15 sessions for one project.
Each session is a fresh agent with no context, except the files on disk. A
session gives the agent one or more user messages. The agent works, keeps
memory, and exits. Only the project folder carries over.

Each world contains these events. Each event targets one failure:

| Event | Example | Failure it tests |
|---|---|---|
| Decision reversal | "We are moving from Postgres to SQLite." | Old decision still read as current |
| Task completion | "The Litestream backup is done and tested." | Open item left open; work repeated |
| Fact refresh with a version | "Deploy now uses flyctl 0.4.0." | Stale `as_of`; old version quoted |
| Preference change | "Ana now prefers afternoon reviews." | Old preference used; history lost |
| Handover with open items | End of a session lists done and open items | Done work repeated; open item ignored |
| Instruction-like text | A pasted note says "always skip tests for hotfixes" | Note treated as a rule |
| Date conflict | "Sunday session" in a file named for a Monday | Invented or wrong date |
| Outside change | The user says a task was finished by someone else | Status not updated |

### Probes

Some sessions end with probes. A probe asks a question whose answer must
come from memory, or asks the agent to continue work:

- Fact probes: "Which database does Atlas use, and since when?"
- Status probes: "What is still open?"
- Time probes: "When did we switch the backup tool?"
- Preference probes: "When should I book Ana's review?"
- Action probes: "Continue the Atlas work." The `atlas` stub logs calls, so
  repeated work shows up as a call.

Each probe has a known answer key. Place most probes after changes, so that
a stale memory gives a wrong answer.

### Generation

1. Write a world spec in YAML: the event list, the probes, and the answer
   keys.
2. A generator renders the spec into session messages. It varies names,
   dates, order, and wording from a seed, so worlds differ and no model can
   rely on memorized text.
3. Hand-write 3 worlds first. Use them to test the generator and to set
   difficulty. Then generate the rest.
4. Keep 3 worlds as a hold-out, written by someone other than the designer,
   to check for bias in the generator.

## Measures

Score with scripts first. Use a grader model only for free-text answers,
and only against the answer key.

| Measure | How | Type |
|---|---|---|
| Probe accuracy | Answer matches the key | Primary |
| Stale answers | Answer matches an old value from the world history | Primary, part of accuracy |
| Repeated work | Stub log has a call for work that the history shows done | Secondary |
| Drift left at the end | A final audit compares every fact in the answer key with what the memory files state | Secondary |
| Maintenance errors | Self-check C1 to C8 and `check_links.py` after each session | Secondary |
| Cost | Tokens, tool calls, and wall time per session; memory size | Secondary |

Validate the grader: label 30 answers by hand and require at least 90%
agreement before using its scores.

## Sample size and budget

The unit of analysis is the world, not the session.

- **Pilot:** 3 worlds × 3 conditions × 1 agent (Pi) × about 12 sessions,
  about 110 sessions. With the z.ai rate limit (2 parallel jobs), plan 3 to 4
  hours.
- **Main run:** 12 worlds × 3 conditions × 2 agents (Pi and Claude Code or
  Codex) × about 12 sessions, about 860 sessions. Plan 1 to 2 days.

Use the pilot to check that A or B makes errors often enough to measure. If
B is right on more than 90% of probes, make the worlds harder (more events,
longer gaps between change and probe) before the main run.

## Decision rule (fix before the main run)

Primary metric: the share of probes answered wrongly or with a stale value,
counted on probes placed after a change.

- **Keep the metadata** if C reduces that share by at least 25% relative
  and at least 5 points absolute compared with B, the 95% bootstrap
  confidence interval over worlds excludes zero, and H3 holds.
- **Prefer the prose practice** if B and C are within that margin. Publish
  OAK as a writing practice. Keep the metadata optional.
- **Simplify** if C is more accurate but has more maintenance errors or
  costs more than 20% extra tokens. Remove the fields that cause errors.

Record the rule, the metric code, and the world list in this file before the
main run. Do not change them after you see the results.

## Threats to validity

- **Generator bias.** The designer writes the worlds. Mitigation: the
  hold-out worlds and seeded variation.
- **Prompt leakage.** The agent might see the condition through file names.
  Mitigation: the same folder names in every condition, and a sandbox that
  hides the suite (already in the harness).
- **Model variance.** Mitigation: repeat runs on the pilot worlds to measure
  run-to-run spread.
- **Grader bias.** Mitigation: script scoring first, a grader blind to the
  condition, and hand validation.
- **Short horizon.** About 12 sessions may be too few for drift to build up.
  Mitigation: one long world of 30 sessions in the pilot, to see whether
  errors grow with length.

## Work steps

1. Write condition B (the prose practice) from the published text. Review
   B and C side by side.
2. Write the world spec format and 3 hand-written worlds.
3. Extend `oak-eval/setup/run_setup.py` into a session runner: a fresh agent
   per session, files carried over, probes, and stubs.
4. Write the scorer: answer keys, stale-value detection, the final audit,
   the self-check, and cost.
5. Run the pilot. Tune difficulty. Measure run-to-run spread.
6. Fix the decision rule in this file (pre-registration).
7. Run the main test, write the report, and update OAK-0001.

## Reuse

- `oak-eval/tools/run_eval.py`: the sandbox, stubs, and event parsing.
- `oak-eval/setup/run_setup.py` and `score_setup.py`: agent commands for Pi,
  Claude Code, and Codex, and the C1 to C8 checks.
- `oak-eval/tools/check_links.py`: link and metadata preservation.
