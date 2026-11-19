# OAK v1 decision brief

Research date: 2026-11-19.

## The problem

A specification tells an agent what to make. Code, content, version
history, and live systems let it inspect what exists. A fresh agent also
needs facts that may exist only in the conversation where the work
started. These include why the owner changed a requirement, who approved
a publication, whether that approval still applies, and what someone
observed on a remote machine.

OAK should give those facts one canonical home and a consistent way to
pass them to the next reader. For example, a content repository can hold
both an edited article and its publication specification. Neither file
necessarily preserves the publisher's decision to delay release in one
market. That decision has to reach the worktree that prepares the release.

## What we know

| Question | Finding | Decision |
|---|---|---|
| Can agents recover stale project state? | Repository accuracy was 91.8% with OAK and 91.5% without. In the stale-state pilot, agents usually checked Git, code, and data. | Point to project sources. Store copies only when an observation itself matters. |
| Do notes matter when the source is absent? | In both Riverport cases, the no-notes agent left permitted work undone. Plain notes passed both. The audit found real losses, including unmerged worktree edits and an overwrite. | Preserve unique facts. Check whether they reach the reader. |
| Does explicit structure help? | Scope questions scored 27/30 with prose and reading rules and 28/30 with a scope field and the same rules. The task prompt invited a wrong-environment check. Structured Markdown also passed the maintenance cases that exposed a free-form note failure. | Standardize meaning and maintenance guidance. An agent accuracy gain from field syntax remains unproven. |
| Do separate records help concurrent work? | In the 36-round pilot, new dated records cut conflicts from 24 to 6, with zero lost records in all layouts. In a follow-up, separate plain and OAK files both merged cleanly and readers used both decisions. | Prefer separate files for concurrent writers. Test delivery failures separately. |

The problem is real. A lightweight convention appears feasible. Its
net value over well-maintained Markdown and ordinary Git workflows
remains unmeasured. We tested mainly GLM 5.3 on one person's projects.
The evidence supports a narrow experiment in portability and delivery.

Sources: [research synthesis](../research.md),
[v0.4 evidence](../publish/evidence.txt),
[handoff results](oak-bench-calibration.md).

## Design options

| Approach | Where it earns its cost |
|---|---|
| Give the model raw transcripts and project access | Works when the source survives, the reader can reach it, and searching costs less than maintaining a handoff. Use this as a baseline when those conditions hold. |
| Use structured Markdown with one location and a writing guide | Supports human review and ordinary Git diffs. The results make this the baseline to beat. |
| Use Markdown with a small machine-readable header | Gives independent tools one way to locate records, check references, and detect missing records. This is the v1 candidate. |
| Use JSON or JSON Lines as the source | Useful when software is the main writer or an event stream is the main interface. Durable shared appends need a write protocol. JSON works well as an export from Markdown if tools need it. |
| Use TypeScript or R as the source | These formats fit executable analysis or configuration. For general project knowledge, a language runtime adds a dependency and mixes record data with executable code unless the format is restricted to data. |
| Use a database or knowledge graph | Fits queries and reconciliation across many records. It adds a service or import and export process that should earn its cost on a demonstrated workload. |

A content hash can detect a byte change when compared with a trusted
digest. It cannot establish approval, scope, freshness, or delivery.
Git can already identify the bytes for a specific revision in repositories.
For transfers outside Git, test a manifest with record identifiers and
optional digests if there is a concrete need to verify the copied bundle.

## Proposed direction

Keep Markdown as the canonical body. Test one small, versioned header
for records that need cross-tool handoff. Start with a stable record
reference, source, scope, and an explicit link when a record replaces or
withdraws another. Preserve the reason in prose. Use a discoverable
shared location. Treat delivery as an observable step: the reader's
copy contains the record or it does not. Start with one mapping and one
reference checker. Add other formats when an integration needs them.

Compare strong structured Markdown and Markdown with an OAK header.
Give both the same facts and reading and writing rules. Run each with
and without the same delivery check. This separates the value of
machine-readable fields from the value of confirming receipt.
Exercise an unmerged worktree, an overwrite during import, and a handoff
to a documentation or content project. Use independent writers and readers.
Measure unique facts that arrive, wrong actions and blocked attempts,
and maintenance cost. Include raw source access where it is realistic.

If reliable detection or recovery follows from the convention at modest
cost, keep the checks that earned their place. If the same workflow with
ordinary Markdown ties on those outcomes, publish OAK as the portable
writing and handoff convention. Keep the header optional.

## Delivery experiment outcome

The checked readers applied the current approval in all four arms.
The unchecked readers followed the stale hold in all four arms.
Repeating the header arms with headers on the older records gave
the same outcome. The host knew the expected path and could recover
the writer's copy. The experiment tested receipt and recovery under
those conditions.

This result gives the receipt rule a reason to be in v1. A sender
names the intended record and destination. A tool or reader confirms
it can read the intended version from that destination. A mismatch
means the handoff needs repair or remains incomplete. A Git revision
or a digest can support the check. Keep the header optional while we
test discovery across independent tools. [Run notes](/notes/2026-11-19-oak-bench-delivery.md)
