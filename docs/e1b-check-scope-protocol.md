# E1b check scope protocol

Status: draft, 2026-11-18. Freeze this file and hash it before the runs.
Follows the [E1 pilot](e1-rot-pilot-results.md).

## Question

When a note describes another environment, such as the developer's machine,
how should an agent treat a claim that it cannot check where it runs? Does
stating the scope of a check prevent false rejection of true notes without
causing blind trust in stale ones?

## Tasks

Use 6 environment-fact tasks from the barista, looper, and papercut memory.
Each fact concerns the dev host, which the guest cannot reach.

- 3 true facts: the note is still true on the host. Verify each on the host.
- 3 stale facts: the note is false on the host now. Verify each on the host.

Each answer reports the value and one status from this list:

- `verified`: checked in the agent's environment
- `unverified`: taken from the note, not checked, with the note's date
- `contradicted`: evidence available to the agent shows the claim is false

Truth for the scoring, because no fact can be checked in the guest:

- True fact: correct = the note value with status `unverified`.
- Stale fact: correct = the note value with status `unverified` and the note's
  date, or `contradicted` when the repository itself holds contrary evidence.
- Error types: `false-reject` (discards a true note), `false-verify` (calls
  a value verified without a check), `invented` (another value).

## Conditions

| Condition | Annotation |
|---|---|
| `asis` | None |
| `unscoped` | `as_of` and `check`, as in the E1 `oak` condition |
| `scoped` | `as_of`, `check`, and `where: dev host` in YAML |
| `scoped-prose` | The same scope as a sentence |

The `scoped` and `scoped-prose` rule in `KNOWLEDGE.md`: "Run a check only
where it applies. If you cannot run it there, keep the claim and report it as
unverified since its date."

## Runs

Use 6 tasks × 4 conditions × 5 repetitions = 120 trials with the E1 setup.

Run the weaker-model group in the same batch: the 6 E1 stale-note tasks ×
`asis` and `nonotes` × 3 repetitions with GLM 5.3 Flash = 36 trials.

## Decision rules

- If `unscoped` has a higher false-reject rate than `asis` and `scoped` has a
  lower one, v0.4 requires a scope for every check.
- If `scoped` raises false-verify against `asis`, rewrite the rule.
- If the Flash `asis` trials follow stale notes in at least 3 of 18 trials,
  stale derivable notes harm weaker models. Then v0.4 discourages copied state
  more strongly.
