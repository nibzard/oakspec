# Offline handoff pilot results

Date: 2026-11-18. This pilot used `claude-zai -p` with GLM 5.3.
Each condition used one setup and two fresh handoff sessions.

| Check | OAK | Plain Markdown |
|---|---|---|
| Preserve the initial decision history | Pass | Pass |
| Select JSON and cite Leo Park's approval | Pass | Pass |
| Apply the later XML approval | Pass | Pass |
| Preserve the CSV, JSON, and XML decision sequence | Pass | Pass |
| Keep local maintenance instructions | Pass, with OAK v0.3 | Pass |

The OAK setup took 127 seconds and 15 tool calls. The plain setup took
56 seconds and 10 calls. The first handoff took 34 seconds and 7 calls
with OAK, and 42 seconds and 7 calls with plain Markdown. The XML update
took 60 seconds and 18 calls with OAK, and 62 seconds and 9 calls with
plain Markdown. These single runs do not establish a typical cost.

Both setups retained the source history in the project. Both agents named
the approver and rejected the unapproved XML proposal at the first handoff.
Both applied the later XML approval and recorded what it replaced. The OAK
setup saved the published specification locally and identified version 0.3.
The plain setup saved its maintenance guidance locally.

The plain current-knowledge file has two broken relative links to the
root decision history. Its index links to that history correctly. Both
agents wrote the original statement that XML was unapproved alongside
the later approval. The OAK decision file and plain current-knowledge file
show the current approval, but the historical statement needs its date
context to avoid confusion. The agents also chose different capitalization
for the configured values. The fixture did not specify accepted casing.

## Limits

- The coordinator fetched the specification and gave its local path to the
  setup agent. This tests use of the published text, not agent retrieval from
  the website.
- Handoff agents had file tools only, with web tools and shell disabled. The
  model service still used the network. The operating system did not enforce
  network isolation or restrict file reads to the project.
  A later test showed that the provider can also supply server-side web tools
  independently of the client tool list.
- The plain guidance was shorter than the OAK specification. Both copies
  began with the same decision facts, but the practices were not equivalent
  in detail. The result cannot isolate the effect of metadata.
- The first two setup sessions were interrupted before they wrote files.
  The completed sessions used a lower effort setting. Times above cover the
  completed sessions only. No human edited the projects during those sessions.
- One simple fixture and one run per condition cannot establish reliability.

Raw project files and event logs are in `/tmp/oak-handoff-pilot/` on this
machine. The files can disappear when temporary storage is cleared.

## Next decision

The local-spec handoff worked in this pilot. Keep the offline requirement
in the next draft, and test agent retrieval from the website separately.
Before making a claim about metadata, run the longer comparison in the
[longitudinal test plan](test-plan-time.md) with equivalent guidance.
