RFC OAK-0001: Open Agent Knowledge

A lightweight, open, format-independent convention for persistent agent knowledge

Field	Value
Status	Experimental — pending evaluation (frozen, see §20)
Version	0.2
Date	2026-11-17
Category	Informational / Proposed Convention
Intended audience	Agent developers, knowledge-tool authors, AI application developers
Reference implementation	Pi agent, optionally
Dependencies	None

⸻

1. Abstract

Open Agent Knowledge (OAK) defines a minimal, interoperable convention for representing persistent knowledge used by AI agents.

Today, agents commonly store knowledge in Markdown files, project documents, handover notes, journals, and loosely structured memory files. These approaches are simple and portable but provide limited explicit information about the meaning, temporal relevance, provenance, and relationships of their contents.

This introduces several problems:

* Historical records may be interpreted as active instructions.
* Completed work may be repeated.
* Superseded decisions may be treated as current.
* Personal memories may become contradictory, duplicated, or difficult to retrieve.
* Knowledge may become trapped in particular agent frameworks.
* Agents may struggle to distinguish original observations from later interpretations.

OAK addresses these problems by defining a small semantic convention that can be expressed in existing formats, including Markdown, KSON, JSON, YAML, and other document representations.

OAK does not prescribe a memory engine, database, ontology, retrieval algorithm, agent runtime, or execution framework.

Its purpose is to make persistent knowledge easier to write, interpret, connect, revise, and transfer between agents.

The central principle is that knowledge describes or specifies something; merely encountering that knowledge does not constitute a new request to act.

⸻

2. Motivation

Agents increasingly operate across long periods, multiple sessions, and changing contexts.

They read and write:

* Project specifications and architectural decisions.
* Execution logs, plans, and handovers.
* Personal preferences and historical observations.
* Research notes, extracted facts, and conclusions.
* Long-running project documentation.
* Shared knowledge maintained by several agents.

Most of this information is already represented as ordinary files.

The problem is not a lack of storage formats. It is the lack of a small, common agreement about what stored information means.

For example:

# Deployment handover
- [x] Applied database migration
- [x] Restarted services
- [x] Notified stakeholders
Remember to restart services after migration.

An agent encountering this document may correctly interpret it as historical context or incorrectly treat its contents as active instructions.

Similarly, a personal agent may encounter conflicting memories:

January: User prefers morning meetings.
March: User no longer prefers early meetings.

Without a convention for distinguishing history from current understanding, both statements may continue influencing the agent equally.

OAK proposes that a small amount of explicit semantics, combined with ordinary natural-language reasoning, can reduce these ambiguities without requiring a complex memory architecture.

3. Design philosophy

OAK follows seven principles.

3.1 Files first

Knowledge SHOULD remain usable as ordinary files.

An agent SHOULD be able to read, search, and edit OAK documents through existing tools such as cat, grep, rg, and file-editing APIs.

No dedicated service is required.

3.2 Format independence

OAK defines meaning rather than syntax.

The same knowledge MAY be represented using Markdown, KSON, JSON, or other formats.

Conforming implementations interpret equivalent metadata consistently regardless of serialization.

3.3 Minimal semantics

OAK standardizes only distinctions that are broadly useful across agent applications.

Domain-specific knowledge structures SHOULD emerge from actual use cases rather than be mandated by the convention.

3.4 Natural language remains first-class

Knowledge does not need to be decomposed into triples, predicates, or rigid schemas.

Narrative notes, reasoning, uncertainty, and contextual explanations are valid knowledge.

3.5 Agents remain intelligent

OAK SHOULD NOT prescribe how agents search, summarize, reason, consolidate memories, or decide which information is relevant.

Those capabilities belong to the agent and may improve with future models.

3.6 Progressive enhancement

A small collection of OAK files requires no additional infrastructure.

Optional indexing, semantic search, graph traversal, schema validation, and specialized tools may be added without changing the underlying knowledge.

3.7 Graceful degradation

Knowledge MUST remain intelligible to humans and general-purpose agents without an OAK-specific runtime.

The loss of an index or optional extension MUST NOT make the source knowledge inaccessible.

⸻

4. Scope

4.1 Goals

OAK aims to:

1. Distinguish historical records, current knowledge, and specifications.
2. Preserve useful temporal context and provenance.
3. Support links and relationships between knowledge resources.
4. Support revision, correction, and supersession.
5. Enable portable knowledge across agent frameworks.
6. Provide a foundation for long-term memory and document-based agent workflows.
7. Require minimal additional conventions and tooling.

4.2 Non-goals

OAK does not attempt to:

* Define an agent operating system.
* Authorize or execute actions.
* Replace agent system instructions.
* Guarantee immunity to prompt injection.
* Guarantee correctness or truthfulness of stored knowledge.
* Require a knowledge graph or vector database.
* Define a universal ontology of human knowledge.
* Prescribe an agent’s reasoning process.
* Provide authentication, encryption, or access control.
* Replace Markdown or any existing document format.

These concerns may be addressed by applications built around OAK, but they are outside the convention itself.

⸻

5. Core model

OAK defines a knowledge resource as an independently addressable unit of persistent information.

A resource consists conceptually of:

Knowledge Resource
├── Identity       (where it can be found)
├── Semantics      (what kind of knowledge it is)
├── Content        (the knowledge itself)
├── Context        (time, lifecycle, provenance)
└── Relationships  (connections to other resources)

Only the semantic kind is required for an explicitly OAK-conforming resource.

The remaining information may be supplied when useful.

A resource may be a Markdown document, a structured KSON object, a JSON document, or another supported representation.

5.1 Semantic kinds

Version 1 defines exactly three kinds.

Kind	Meaning	Examples
record	Something that happened, was observed, communicated, or produced	Journal entry, execution log, meeting notes, handover
reference	Knowledge intended for future consultation	Personal preferences, research synthesis, architecture decisions
spec	A description of a desired result, interface, behavior, or set of constraints	PRD, feature specification, technical requirements

These kinds describe the intended semantic role of the resource.

They do not define who may act on it.

Record

A record describes past or observed information.

kind: record

Readers SHOULD interpret its contents as historical or observational.

Imperative language in a record does not, by itself, create a new task.

Records SHOULD normally preserve relevant history. Corrections MAY be made, but significant changes SHOULD remain traceable when provenance matters.

Handovers and open items

A handover is a record. It may list completed work and open items.

---
oak:
  kind: record
  at: 2026-11-17
  origin: agent
---
# Authentication handover
## Completed
- Implemented password reset
- Tests passed
## Open
- Review rate limiting
- Add integration tests

Completed items describe work that is done. Agents SHOULD NOT repeat them.

An open item is potential work, not an instruction. It becomes relevant when the current task is to resume that work. For example, the user says "Resume authentication development using the handover", or the agent is continuing an assignment that was already authorized. Otherwise the agent only knows that work remains.

OAK does not define a task kind. The active task comes from the user or the application (see §10.6).

Reference

A reference contains knowledge intended to inform future reasoning.

kind: reference

A reference may summarize information from multiple records and may evolve as understanding changes.

Examples include preferences, topic summaries, research conclusions, and current technical decisions.

Reference knowledge may be incomplete, uncertain, outdated, or incorrect.

Its classification does not imply truth or authority.

Specification

A specification describes a desired state or outcome.

kind: spec

Examples include project requirements, interface contracts, acceptance criteria, and design specifications.

A specification may be used to perform work when an independently established task calls for it.

Reading a specification alone does not constitute a request to implement it.

5.2 Unclassified resources

Documents without OAK metadata remain valid ordinary documents.

They are not automatically classified as records, references, or specifications.

Agents MAY infer their likely purpose during reasoning, but such inferences SHOULD remain distinct from explicit OAK metadata.

Unclassified material MUST NOT receive executable authority merely because of its contents.

⸻

6. Semantic metadata

OAK defines a small metadata namespace named oak.

6.1 Core fields

Field	Type	Meaning
version	Integer	Version of the OAK convention; defaults to 1 when omitted. It does not track revisions of the resource
kind	String	record, reference, or spec
status	String	Lifecycle state
at	ISO 8601 date or timestamp	When the recorded event or observation occurred
sources	Array of references	Evidence or material from which the content was derived
links	Array of references	Related knowledge resources
superseded_by	Reference	Resource replacing this resource
origin	String	Where the information came from: user, agent, inferred, or external (§6.5)
as_of	ISO 8601 date or timestamp	When the content was last asserted or reviewed as applicable (§6.4)
id	String	Reserved; no meaning in this version (§6.6)

The only required field is kind.

version SHOULD be included by tools that generate OAK documents.

6.2 Lifecycle status

Version 1 recommends four lifecycle values:

* draft — not yet finalized.
* current — considered applicable or relevant.
* superseded — replaced by newer information.
* archived — retained primarily for historical access.

Status is optional. Absence of status MUST NOT be interpreted as proof that a resource is current.

Additional application-specific values are permitted, but unknown values MUST NOT be assigned invented semantics by generic OAK tooling.

Status and kind represent different properties.

For example:

kind: spec
status: current

means the specification is considered current.

It does not mean an agent is currently instructed to implement it.

Similarly:

kind: record
status: archived

remains a historical record.

6.3 Provenance

The sources field identifies resources that support, explain, or contributed to the content.

Examples:

sources:
  - ../journal/2026-11-17.md
  - ../conversations/session-42.md

Sources MAY be local paths or external URIs.

A source reference does not guarantee that a claim is correct. It provides a way to inspect where the claim came from.

Provenance SHOULD be preserved when information is summarized, consolidated, or revised.

6.4 Temporal meaning

OAK has two time fields. Each one applies to different kinds.

The at field denotes the date or time of the event or observation described by a record.

It is not automatically the file creation time.

The as_of field applies to references and specifications. It is the date when the content was last asserted or reviewed as applicable.

It is not the file modification time. A typo fix does not change as_of. as_of does not guarantee correctness and does not imply expiry. It lets a later agent judge the age of the knowledge and decide whether the task calls for a new check.

Records do not use as_of. The content of a record belongs to its at.

If the relevant date is unknown, authors SHOULD omit it rather than invent one.

The split follows the distinction between valid time and transaction time in bitemporal data (Appendix B).

Applications needing richer temporal modeling MAY use additional domain-specific fields.

6.5 Origin

The origin field states where the information came from. It describes the source of the knowledge, not who wrote the file.

* user — the information came from the user, even if an agent wrote the file.
* agent — the agent observed or produced it, for example a tool result or an execution log.
* inferred — the resource mainly holds an interpretation derived from other information. It SHOULD list sources.
* external — a third party produced it, for example a web page, an email, or a vendor document. The user or agent only captured it.

origin is optional. When a resource mixes origins, authors SHOULD omit origin and keep the distinction in the content and in sources. Do not assign one origin to the whole resource.

origin does not grant trust or authority. External content in particular can contain text that claims authority (§10.1).

6.6 Reserved identifier

The id field is reserved for a future stable identifier. Version 1 assigns it no meaning.

An id alone does not make references safe across renames. That needs a resolution convention or a link-rewriting tool, which is outside this version (Q2).

6.7 Extensibility

Applications MAY define additional metadata.

Custom extensions SHOULD be namespaced to avoid conflicting with future core fields.

Domain-specific content MAY use the host format’s normal structures outside the oak namespace.

Generic readers MUST ignore unknown extension fields they do not understand and SHOULD preserve them when rewriting documents.

⸻

7. Format mappings

OAK intentionally does not define a new serialization language.

It defines a semantic model that host formats can represent.

7.1 Markdown

Markdown documents MAY use YAML frontmatter containing the oak namespace.

Example:

journal/2026-11-17.md

---
oak:
  version: 1
  kind: record
  at: 2026-11-17
  links:
    - ../topics/coffee.md
    - ../topics/sleep.md
---
# November 17
Had coffee around 15:00.
Went for a 40-minute walk.
Mentioned difficulty sleeping the previous night.

The Markdown body remains ordinary Markdown.

Existing editors, renderers, and shell tools continue to work.

If a document already has frontmatter, the oak key can coexist with its existing metadata.

7.2 Structured formats

KSON, JSON, and other structured formats MAY carry the same oak fields. Appendix A shows a non-normative KSON example.

7.3 JSON

Equivalent information may be represented as:

{
  "oak": {
    "version": 1,
    "kind": "record",
    "at": "2026-11-17",
    "links": [
      "../topics/coffee.json",
      "../topics/sleep.json"
    ]
  },
  "content": "Had coffee around 15:00."
}

The logical semantics are the same.

7.4 Sidecar metadata

For formats where embedded metadata is undesirable or unsupported, OAK MAY use an adjacent sidecar.

Example:

spec.md
spec.md.oak.json

The sidecar contains:

{
  "oak": {
    "version": 1,
    "kind": "spec",
    "status": "current"
  }
}

This allows existing documents to participate without modifying their contents.

A resource SHOULD have exactly one authoritative OAK metadata representation. Implementations SHOULD flag conflicting embedded and sidecar metadata instead of silently merging them.

7.5 Representation neutrality

Consumers SHOULD normalize supported representations to the same conceptual model.

A conforming resource’s meaning MUST NOT depend on whether its metadata came from Markdown frontmatter, KSON fields, JSON fields, or a sidecar.

Host-format-specific features remain available but are not required for OAK interoperability.

⸻

8. Relationships and navigation

OAK uses references to connect knowledge resources.

A reference may be:

* A relative file path.
* An absolute URI.
* A path with a fragment identifying a section or anchor.

Relative file references resolve against the containing resource’s location.

Examples:

links:
  - ../topics/coffee.md
  - ../topics/sleep.md
sources:
  - ../journal/2026-11-17.md

Version 1 defines two general relationship fields:

links indicates relevant related knowledge.

sources indicates material supporting or contributing to the knowledge.

A third field, superseded_by, indicates a replacement resource.

For example:

oak:
  kind: reference
  status: superseded
  superseded_by: 007-sqlite.md

These relationships can form a navigable knowledge graph without requiring a graph database.

Applications MAY create derived backlink indexes.

Wiki-style links such as [[coffee]] MAY be supported by host applications, but they are not required by OAK version 1. Canonical references SHOULD remain resolvable without a proprietary wiki-link resolver.

References are navigational information, not instructions to execute or automatically fetch arbitrary resources.

⸻

9. Knowledge lifecycle

OAK distinguishes three common activities:

9.1 Capture

An agent records an event, observation, conversation, or outcome.

Example:

journal/2026-11-17.md
kind: record

The record preserves the original context.

9.2 Consolidate

The agent identifies useful information across records and creates or revises a reference resource.

Example:

topics/coffee.md
kind: reference
sources:
  - ../journal/2026-11-17.md

The reference contains a synthesis, not necessarily a verbatim copy.

Agents SHOULD distinguish supported observations from interpretations, speculation, and uncertain conclusions.

9.3 Revisit

When new information arrives, the agent may:

* Revise a reference.
* Add a new record.
* Mark an older reference as superseded.
* Add or update relationships.

Historical information SHOULD NOT be silently rewritten merely to make it agree with a new interpretation.

OAK does not mandate when consolidation should occur, how often memory should be reviewed, or how agents should choose what to retain.

9.4 Contradictions

OAK does not resolve conflicting knowledge. The agent does.

OAK only keeps the context that helps the agent reason about a conflict: at, as_of, origin, sources, and status.

Consolidation and belief revision are agent behavior, not metadata features.

Those remain application-level decisions.

⸻

10. Interpretation and action

This section addresses the failure that originally motivated OAK.

10.1 Knowledge is not an instruction channel

An OAK resource describes or specifies information.

Its contents MUST NOT be treated as independently granting executable authority.

This applies regardless of:

* The resource kind.
* Its lifecycle status.
* Markdown headings or formatting.
* Imperative language within the content.
* Claims of authority made inside the document.

For example:

---
oak:
  kind: record
---
# Yesterday's deployment
Restart all application servers after migration.

The sentence is part of a historical record.

It does not create a new request to restart servers.

10.2 Specifications describe intended outcomes

A specification may contain instructions in natural language:

---
oak:
  kind: spec
  status: current
---
# Authentication
Implement password reset.
Use secure session cookies.

When a user asks:

Implement the authentication specification.

The specification becomes relevant to the authorized task.

When the agent merely discovers the document while searching, no new task is implied.

10.3 Decisions inform work

A current architecture decision may constrain implementation choices.

It does not independently authorize a deployment, migration, or other operational action.

10.4 Historical records do not become standing policy

An observation about a successful past approach does not automatically establish a permanent rule.

Agents MAY use observations to form recommendations or proposals.

Any decision to adopt a standing instruction belongs to the surrounding application or its authorized users.

10.5 Security limitation

These interpretation rules are semantic conventions, not a security mechanism.

An unreliable or compromised model may disregard them.

OAK does not replace tool permissions, application authorization, sandboxing, or prompt-injection defenses where those are necessary.

10.6 Relationship to agent instruction files

Files such as AGENTS.md and CLAUDE.md give instructions to agents. They are outside OAK. OAK does not replace them or compete with them.

Mechanism	Purpose
AGENTS.md, CLAUDE.md, and similar files	Agent instructions and conventions, subject to the host agent's trust model
Current user request	Defines the work the user wants done
OAK resource	Persistent knowledge to consult when relevant
Agent runtime	Decides how information is supplied and which operations are permitted

A file name or embedded metadata does not make a document trustworthy.

A host can load a knowledge file as instructions, for example through an import in CLAUDE.md. In that case the host's loading mechanism gives the file authority, not OAK.

⸻

11. Memory organization

OAK does not prescribe a mandatory directory structure.

A recommended starting point is:

knowledge/
├── index.md
├── journal/
│   └── 2026-11-17.md
├── topics/
│   ├── coffee.md
│   └── sleep.kson
├── people/
│   └── preferences.md
├── projects/
│   └── atlas/
│       ├── spec.md
│       ├── handover.md
│       └── decisions/
│           └── 001-database.md
└── research/
    └── agent-memory.md

This structure distinguishes chronological information from topic-oriented knowledge.

It is illustrative, not normative.

Agents MAY create, rename, merge, or split resources as needed.

Resource granularity is intentionally unspecified.

A journal containing an entire day is valid. A single observation in its own file is also valid.

OAK version 1 does not mandate statement-level knowledge representation.

Discovery

Agents SHOULD be able to discover and search OAK knowledge using ordinary filesystem operations.

An index, manifest, graph database, or search service MAY improve discovery but MUST NOT be required to interpret an individual resource.

⸻

12. Agent interoperability

Knowledge SHOULD survive changes in agent implementation.

An agent using OAK should be able to receive an existing knowledge directory and:

1. Discover relevant resources.
2. Understand the meaning of supported metadata.
3. Retrieve and interpret their contents.
4. Follow relationships.
5. Update resources without unnecessarily discarding history or unknown metadata.

No agent-specific tool protocol is mandated.

An application MAY expose commands such as:

oak search "coffee and sleep"
oak links topics/coffee.md
oak check

These utilities are optional.

They may use full-text indexing, structured parsing, or semantic retrieval.

Derived indexes SHOULD be reconstructible from the canonical resources.

OAK does not standardize a retrieval API in version 1.

⸻

13. Compatibility and adoption

OAK is designed for incremental adoption.

Existing knowledge repositories do not require a complete migration.

A project may begin by annotating a single Markdown document:

oak:
  kind: spec

Additional metadata can be introduced when it provides value.

Existing documents without OAK metadata remain ordinary documents.

Applications SHOULD allow non-OAK and OAK resources to coexist.

An OAK implementation MUST NOT require every resource in a repository to adopt the convention.

This is important for compatibility with existing project repositories, Markdown wikis, knowledge-management tools, and general-purpose agents.

⸻

14. Conformance

OAK version 1 defines two minimum conformance levels.

14.1 OAK-compatible resource

A resource is OAK-compatible if:

* It has an accessible representation.
* It declares a supported oak.kind.
* Its metadata can be mapped to the OAK semantic model.

Additional metadata is optional.

14.2 OAK-compatible consumer

A consumer is OAK-compatible if it can:

* Recognize all three core kinds.
* Interpret supported metadata fields according to their defined meaning.
* Distinguish knowledge resources from independent requests for action.
* Resolve supported resource references.
* Ignore unknown extension metadata without assigning it unintended semantics.

Consumers that write resources SHOULD preserve supported and unknown metadata where feasible.

14.3 Optional capabilities

Implementations MAY additionally support:

* Structured search.
* Backlink discovery.
* Graph navigation.
* Schema validation.
* Memory consolidation.
* Duplicate detection.
* Semantic indexing.
* Provenance visualization.
* Conflict analysis.
* Knowledge synchronization.

None are required for baseline conformance.

⸻

15. Privacy and safety considerations

Persistent knowledge may include sensitive personal information, including health observations, financial information, communications, and private project material.

OAK does not define storage security or sharing permissions.

Implementations SHOULD respect the surrounding environment’s access controls and user privacy expectations.

Agents SHOULD avoid recording unnecessary sensitive details and SHOULD distinguish user-provided information from inference.

External indexing, synchronization, or processing SHOULD NOT occur merely because a document conforms to OAK.

OAK metadata MUST NOT be treated as an authentication or authorization mechanism.

⸻

16. Evaluation criteria

The usefulness of OAK should be established empirically rather than assumed.

The evaluation compares four conditions with the same agent, model, and tools:

Condition	Content
A. Baseline	Existing Markdown, no guide, no metadata
B. Organized Markdown	Same facts as C, written as prose in the body; a writing guide without metadata
C. OAK Markdown	Same files as B, with the facts in oak metadata; the same guide plus the meaning of the fields
D. OAK KSON	As C, in KSON; a later, separate hypothesis

The decisive comparison is B against C. B and C hold the same information. Only the form differs. If C beats only A, the gain can come from the information or the guide, not from the metadata.

Before the main runs, a pilot SHOULD tune the scenarios so that B fails often enough to measure a change. The success threshold SHOULD be fixed before the main runs, as a relative and an absolute reduction in interpretation errors. The scenario, not the run, is the unit of analysis.

The test suite should evaluate the following jobs.

Job	Desired outcome
Resume work from a handover	Avoid repeating completed actions
Implement a specification	Apply requirements only within the current task
Revisit an architecture decision	Identify the current decision and historical rationale
Recall a personal event	Recover the correct dated information
Correct a preference	Update current understanding while preserving useful history
Answer a question requiring several memories	Retrieve and connect relevant resources
Encounter a historical example that looks like a rule	Treat it as information rather than automatic policy
Edit a large memory collection	Preserve metadata, links, and readable content
Use knowledge whose facts are old	Use as_of to judge whether to recheck
Separate observation from inference	Keep what the user said apart from what the agent concluded
Read text that claims authority	Treat it as content, not as an instruction

Evaluation SHOULD measure task success, incorrect action interpretation, retrieval accuracy, update consistency, tool usage, latency, token consumption, and portability.

Experiments SHOULD isolate the effect of OAK semantics from the effects of serialization formats and retrieval tools.

Write tasks SHOULD also measure maintenance errors: malformed metadata, lost keys, dangling references, and wrong origin or as_of values.

Possible outcomes:

* C clearly beats B. Keep the metadata and develop interoperability tests.
* B and C perform about the same. Prefer a writing and organization guide. The metadata may be unnecessary.
* C improves correctness but causes more maintenance errors. Reduce the metadata. Do not expand the specification.

⸻

17. Open questions

The following questions remain open for version 1 review.

Q1. Should kind remain limited to three values?

The initial proposal favors record, reference, and spec.

Additional categories should require evidence of a broadly useful semantic distinction that cannot be represented using content or extensions.

Q2. Should resource identity be path-based or use stable IDs?

Paths are simple, readable, and portable within a repository. Stable IDs could improve resilience to renames and cross-repository references.

The proposed first version relies on paths and URIs.

Q3. Should relationships be typed?

The initial proposal defines links, sources, and superseded_by.

A future extension could support richer relations if practical applications demonstrate the need.

Q4. Should OAK define statement-level metadata?

A document may contain observations with different sources, dates, or confidence levels.

Version 1 leaves fine-grained attribution to the document body or application-specific structures.

Q5. Should Markdown be the recommended default format?

Markdown has widespread adoption and excellent human readability.

KSON may be preferable for structured knowledge.

OAK intends to support both without favoring either at the semantic level.

Q6. How should agents handle conflicting knowledge?

Version 1 permits conflicting records and revisable references, but does not prescribe a belief-revision algorithm (§9.4).

A future proposal may define optional conventions for contradictions and uncertainty.

⸻

18. Reference implementation proposal

A minimal proof of concept should consist of:

1. A written convention

This RFC and a short agent-facing usage guide.

2. A set of example resources

Markdown and KSON files covering personal memory, project specifications, architecture decisions, and handovers.

3. A small interoperability test suite

Checks for semantics, links, lifecycle updates, and preservation through edits.

4. An optional CLI

A utility that can inspect metadata, resolve links, and search resources.

An initial implementation may use Pi as a test environment because agents can work directly with files using existing tools.

No new agent-specific tool is required for the first experiment.

The implementation should not expand into a memory service, execution kernel, or general-purpose agent framework without independent evidence that those capabilities are needed.

⸻

19. Future evolution

OAK should evolve through small, independently useful extensions.

Potential future proposals include:

* OAK Links — stable resource identifiers and richer relationships.
* OAK Sources — fine-grained provenance and evidence anchors.
* OAK History — revision and supersession conventions.
* OAK Search — a portable retrieval interface.
* OAK Collections — manifests and discovery for large repositories.

Extensions must remain optional wherever possible.

The base convention should remain small enough to understand without specialized software.

The goal is not to make OAK responsible for every aspect of agent knowledge.

The goal is to establish a durable common foundation that increasingly capable agents can use in their own ways.

⸻

20. Decision requested

This RFC proposes the following minimal core for experimentation.

This draft is frozen. No new kinds or fields will be added until the evaluation in §16 reports.


1. Three semantic kinds: record, reference, spec.
2. One metadata namespace: oak.
3. Optional context fields: status, at, as_of, origin, sources, links, and superseded_by; id reserved.
4. Format-independent representation: Markdown in examples; KSON, JSON, and other formats permitted.
5. No implicit execution semantics: knowledge does not independently create requests or permissions.
6. File-first operation: no mandatory runtime, database, or dedicated agent tool.

All further functionality should be justified by observed use cases and measured improvements.

Closing principle

Knowledge should remain intelligible and useful independently of the agent that created it.

A good agent knowledge convention should preserve information, meaning, relationships, and history without prescribing how intelligence must operate on them.

OAK proposes the smallest shared vocabulary needed to begin achieving that goal.

⸻

Appendix A. KSON example (non-normative)

A KSON document MAY represent the same semantics through ordinary fields.

journal/2026-11-17.kson

oak: {
  version: 1
  kind: record
  at: '2026-11-17'
  links: [
    '../topics/coffee.kson'
    '../topics/sleep.kson'
  ]
}
content: %markdown
  # November 17
  Had coffee around 15:00.
  Went for a 40-minute walk.
  Mentioned difficulty sleeping
  the previous night.
  %%

KSON is especially suitable when structured information and natural-language content need to coexist.

The content field is a recommended convention for prose-bearing structured documents, not an OAK requirement.

An OAK-aware KSON document may contain domain-specific structured fields in addition to its metadata.

⸻

Appendix B. Prior art

OAK borrows established ideas. It does not claim to invent them.

* Architecture Decision Records (ADRs) keep decisions with their rationale and status, and mark old decisions superseded instead of deleting them. OAK's status and superseded_by follow this practice. See https://adr.github.io/.
* Diátaxis classifies documentation by purpose: tutorials, how-to guides, reference, and explanation. OAK uses a smaller split by purpose for agent knowledge. See https://diataxis.fr/.
* Bitemporal data separates valid time (when a fact was true) from transaction time (when it was recorded or asserted). at and as_of follow this split.
* W3C PROV models provenance (wasDerivedFrom, wasAttributedTo). sources and origin are a minimal subset. See https://www.w3.org/TR/prov-overview/.
* AGENTS.md and CLAUDE.md carry agent instructions. OAK stays outside them (§10.6). See https://agents.md/.

The possible new contribution is narrow. OAK applies one small purpose split to agent knowledge across personal memory, project documents, and agent activity. The evaluation in §16 tests whether that is worth a convention.

End of RFC OAK-0001, experimental version 0.2.
