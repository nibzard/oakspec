# OAK v0.4+: Decision Research for a Durable Open Agent Knowledge Convention

## Executive recommendation

**OAK should continue to exist, but it should become smaller, more explicit about what it is, and more demanding about evidence before it calls itself a standard.** The strongest version of OAK is not “a memory system for agents.” It is a **portable semantic convention for durable knowledge artifacts that may be read and maintained by humans and heterogeneous agents**. That positioning is substantially more defensible.

The published v0.3 draft already contains the right instinct. It separates historical records, current beliefs, and desired state; distinguishes event time from checking time; records provenance and supersession; makes Markdown the human-readable substrate; and explicitly says that knowledge is not an instruction channel. It also describes itself as “habits plus a few lines of metadata,” not a database or retrieval engine. citeturn842546view0

The case for OAK is therefore **not** that models cannot understand ordinary notes. Increasingly capable models often can. Long-context models now accept very large contexts, retrieval systems increasingly organize memory automatically, and agentic memory systems increasingly perform consolidation, linking, search, and rewriting themselves. Google documents million-token-class context as mainstream in its Gemini stack, while Anthropic currently documents up to one-million-token contexts in its platform. Research such as Mem0, A-MEM, Zep/Graphiti, and Letta is explicitly moving memory management into learned or agent-driven mechanisms. citeturn146060search9turn146060search22turn263677academia8turn263677academia9turn567627academia10turn263677search6

The case for OAK is instead that some facts **cannot be reconstructed reliably from intelligence alone**. A future model can infer that a note *looks* obsolete, but it cannot know with certainty when a human verified it. It may infer who probably authored a conclusion, but cannot recover a provenance fact that was never recorded. It cannot know that information was deliberately revoked if every trace of the revocation disappeared. It cannot reliably distinguish “this happened on March 2” from “we learned about this on March 9” when the source did not preserve that distinction. These are information-loss problems, not reasoning problems.

That distinction is the central design principle I recommend for v0.4:

> **Standardize information that cannot be reconstructed after the fact; leave reasoning, retrieval, organization, and workflow to increasingly capable agents and tools.**

This is also the most defensible interpretation of Rich Sutton’s Bitter Lesson. Sutton’s argument was that general methods exploiting computation tend to win over hand-engineered representations of domain knowledge. A large, prescriptive agent-memory ontology therefore has poor long-run prospects. A tiny convention that preserves otherwise-lost provenance, temporal, lifecycle, and authorship information is different: it supplies information to computation rather than substituting hand-designed reasoning for computation. citeturn567627search1

My recommended v0.4 direction is consequently conservative:

**Keep:** `kind`, temporal semantics, provenance/source links, supersession, explicit lifecycle status where needed, human-readable Markdown, and the knowledge-vs-authority boundary.

**Strengthen:** deletion/revocation semantics, source/actor semantics, concurrency expectations, definitions of `at` versus `as_of`, stable identity as an interoperability profile, and conformance rules.

**Demote or remove from the normative core:** folder layout, `index.md`, generic `links`, specific setup procedures, daily journals, end-of-session maintenance rituals, and product-specific instruction-file wiring. These are useful practices but are not universal knowledge semantics.

**Defer:** claim-level RDF-like provenance, rich typed relationship ontologies, graph schemas, embedding formats, search APIs, synchronization protocols, trust scoring, automatic conflict resolution, distributed locking, and executable policy semantics.

Most importantly, **do not promote OAK beyond experimental based on the Papercut study.** The reported 0.918 versus 0.915 accuracy difference is practically negligible and statistically non-significant; the observed 21% reduction in turns and 24% reduction in tool calls are interesting efficiency signals but, as described, are also non-significant and come from a near-ceiling, single-repository setting. The longitudinal freshness hypothesis—the problem OAK is most plausibly designed to solve—has not yet been demonstrated. The current spec itself acknowledges that the principal anecdotal failure observed across one person’s approximately 6,000 agent sessions was stale notes rather than agents fundamentally failing to interpret notes. citeturn842546view0

The next version should therefore be treated as a **hypothesis-refining version**, not a stabilization release.

## What persistent agent knowledge actually fails at

The literature supports some memory failure classes strongly, some indirectly, and some mainly as engineering hypotheses. Treating all of them as equally established would lead OAK toward unnecessary complexity.

Long-term memory benchmarks provide strong evidence that persistent conversational systems struggle with information extraction across sessions, temporal reasoning, updates, multi-session synthesis, and knowing when to abstain. LongMemEval was designed specifically around those five abilities, while LoCoMo evaluates long-term conversational memory over extended conversations and includes question answering, temporal/event understanding, summarization, and multimodal dialogue. citeturn428641search1turn428641search2

Long context does not simply eliminate retrieval problems. *Lost in the Middle* showed substantial positional sensitivity even in models designed for long inputs, with information near the beginning and end often used more reliably than information buried in the middle. RULER similarly evaluates long-context behavior beyond simple needle retrieval, illustrating that nominal context-window size and effective usable context are different concepts. citeturn428641search3turn428641search4

Persistent memory also creates a concrete security problem rather than merely a hypothetical one. 2026 work on memory poisoning shows that malicious content persisted in memory can affect later sessions. *Bad Memory* evaluated Claude Code and Codex across multiple models and found that already-planted malicious memory could influence current and future sessions. MPBench reports systematic vulnerabilities in persistent-memory write channels, and MemSecBench reports malicious-memory persistence in 84.2% of evaluated cases across its 24 configurations, with a successful write-to-execute chain in roughly half of all cases. These numbers should not be generalized to all agents, but the existence of the vulnerability is now empirically well supported. citeturn879756academia0turn879756academia3turn879756academia1

This matters for OAK because v0.3’s R1—“knowledge is not instructions”—is a good semantic rule but **not a security boundary**. OAK correctly says this itself. A host can still inject file contents into a privileged prompt, and a model can still interpret malicious prose behaviorally despite metadata saying otherwise. OWASP now explicitly treats persistent memory poisoning as an agent security concern, and Microsoft describes memory and context stores as security-sensitive. citeturn842546view0turn146060search3turn146060search5

Deletion is becoming similarly important. Recent work evaluates whether “forgetting” a memory actually returns agent behavior to the counterfactual state in which the information had never been stored, rather than merely removing one visible record. That framing exposes an important OAK issue: `W5` currently says to supersede rather than delete unless the user requests deletion. For ordinary history preservation that is sensible, but a user-requested deletion must override preservation norms, including derived summaries where practical. OAK cannot guarantee erasure from Git history, backups, embeddings, or external memory stores, so it should make a narrower but explicit promise about the OAK knowledge set itself. citeturn146060search28

Multi-agent concurrency is less empirically settled but structurally plausible. A 2026 ICML position paper argues that stale reads, lost updates, and inconsistent shared state in multi-agent systems should be treated as concurrency-control problems rather than solved only by prompting. This is not yet evidence that OAK needs transactions or locking; it is evidence that OAK should **not pretend that a shared folder alone solves concurrent authorship**. citeturn146060search4

The resulting failure taxonomy is:

| Failure | Evidence strength | Root cause | Does OAK metadata plausibly help? |
|---|---|---|---|
| Relevant knowledge not retrieved | Strong | Retrieval/context selection | Only indirectly; indexing may help, but retrieval belongs outside core |
| Correct information buried in long context | Strong | Effective-context limitations | Weakly; concise artifacts help but schema is not the main solution |
| Stale current-state beliefs | Moderate for general agents; strong as design concern | No explicit update/freshness lifecycle | **Yes; this is OAK’s strongest target** |
| Conflicting versions interpreted as simultaneously current | Moderate | Missing lifecycle and temporal metadata | **Yes** |
| Completed work repeated | Plausible, weakly quantified | Stale plans/task-state ambiguity | Possibly, but upkeep routines may matter more than syntax |
| Wrong provenance/user-vs-agent attribution | Strong conceptual basis; limited benchmark incidence | Provenance discarded at write time | **Yes** |
| Event time confused with observation/check time | Strong database precedent; agent incidence incompletely measured | Temporal dimensions collapsed | **Yes** |
| Hallucinated/false memory | Strong in memory literature | Faulty extraction or consolidation | Metadata helps auditability, not truth itself |
| Prompt injection via memory | Strong and growing | Untrusted content gains behavioral influence | Metadata is insufficient; authority separation helps architecture |
| Privacy/deletion failure | Emerging empirical evidence | Derived copies and persistent storage | Core semantics should help express revocation, not promise complete erasure |
| Lost updates/concurrent writers | Structural evidence, emerging research | No concurrency control | OAK should acknowledge, not implement transactions |
| Migration/link breakage | Ordinary engineering certainty | Path-based identity | Stable IDs can help interoperability |
| Context/token overhead | Strong practical concern | Too much memory/context | Minimal metadata matters; automatic retrieval remains external |
| Long-horizon semantic drift | Plausible and partially benchmarked | Repeated summarization/update errors | OAK may make drift auditable; prevention remains unproven |

This analysis changes the product thesis. The critical failure is not “agents need a schema to understand notes.” The critical failure is:

> **durable state loses temporal, provenance, lifecycle, and authority information faster than future agents can reconstruct it.**

That is a much narrower and stronger problem statement.

## Alternatives and where OAK is actually differentiated

OAK should not present RAG, Mem0, Letta, Graphiti, long context, AGENTS.md, MCP, ADRs, and W3C PROV as competitors doing the same thing. They occupy different layers.

RAG is fundamentally a retrieval architecture. The original RAG work combines parametric generation with retrieved non-parametric knowledge and demonstrated gains on knowledge-intensive NLP tasks; it does not define how mutable project knowledge should represent status, supersession, ownership, or freshness. citeturn428641search9

MemGPT/Letta is a runtime memory architecture. MemGPT introduced tiered memory managed by the model, while contemporary Letta exposes persistent memory blocks, semantic archival memory, a Git-backed memory filesystem, and automated “dreaming” workflows that consolidate memory. This is much closer to a full memory operating system than to OAK. citeturn567627search2turn263677search2turn263677search6turn263677search7

Mem0 performs automatic extraction, consolidation, retrieval, and optionally graph-backed memory. Its paper reports substantial latency and token-cost reductions relative to full-context baselines on LoCoMo and improved judged response quality. Those claims are system-specific, but they demonstrate the direction of the field: more memory organization will increasingly be performed automatically. citeturn263677academia8

Zep/Graphiti explicitly models temporal relationships in a knowledge graph and reports results on DMR and LongMemEval. Its core problem—dynamically maintaining temporal relationships across conversational and enterprise information—is closer to OAK’s stale-state concern, but its assumptions are much heavier: graph construction, a service/runtime, entity extraction, and graph retrieval. citeturn567627academia10turn263677search0

A-MEM takes the opposite philosophical direction from a static taxonomy. It lets the agent dynamically generate attributes, links, contextual descriptions, and evolving associations, inspired by Zettelkasten. That is exactly the kind of capability that could make parts of an OAK ontology unnecessary as model intelligence improves. citeturn263677academia9

Generative Agents, Reflexion, and Voyager demonstrate three other roles for memory: experiential records and reflections, verbal lessons learned from task feedback, and reusable skills respectively. They support the broad idea that persistent experience can improve future behavior, but they do not establish OAK’s particular three-kind taxonomy. citeturn567627search4turn567627search5turn567627academia12

LangGraph deliberately separates checkpointed thread state from cross-thread long-term stores and describes semantic, episodic, and procedural memories. Its documentation also acknowledges that updating profiles and collections introduces tradeoffs and that no single long-term-memory organization is universally best. That is strong evidence against OAK trying to standardize runtime memory architecture. citeturn567627search6turn263677search3

MCP is an interoperability transport/context protocol, not a durable-knowledge semantics. The current specification gives servers a standard way to expose resources to clients, while the July 2026 release strengthened a stateless protocol core, caching, authorization, and extensions. OAK could eventually be exposed *through* MCP resources, but it should not duplicate MCP discovery, transport, or authorization. citeturn567627search7turn263677search4

AGENTS.md and CLAUDE.md illustrate the adoption advantage of minimally structured Markdown. AGENTS.md deliberately has no required schema and describes itself as a predictable place for agent-facing instructions; its site says it is used across tens of thousands of open-source projects. Claude Code similarly loads hierarchical Markdown memory/instruction files and supports imports. Their success argues strongly for simple files and predictable locations, but also shows why OAK must maintain its separate “knowledge is not instructions” identity. citeturn567627search8turn263677search5

ADRs are especially relevant prior art. They retain individual decisions, statuses, and supersession while staying human-readable. Event sourcing provides another key analogy: storing state changes as an event sequence preserves history and makes replay/reconstruction possible. Temporal databases distinguish transaction time from valid time, showing that collapsing multiple temporal concepts is a longstanding source of ambiguity rather than an agent-specific problem. citeturn428641search7turn146060search19turn146060search34

W3C PROV demonstrates the opposite end of the design spectrum: a rich provenance model covering entities, activities, agents, derivations, responsibility, collections, and provenance-of-provenance. JSON-LD provides a standardized linked-data serialization with interoperability across systems. These are useful conceptual sources but also warnings: OAK can borrow semantic distinctions without importing an ontology that ordinary Markdown users will not maintain. citeturn428641search6turn428641search5

YAML front matter is already an established convention in Markdown tooling such as Jekyll, so OAK’s use of a small front-matter namespace is conventional rather than exotic. citeturn428641search8

The competitive landscape is therefore:

| Approach | Primary problem | Automatic? | Human-readable / portable | Temporal/provenance semantics | OAK relationship |
|---|---|---:|---:|---:|---|
| Long context | Keep more raw information available | Yes | N/A | No | Reduces retrieval pressure; does not recreate missing metadata |
| RAG | Retrieve relevant external knowledge | Yes | Depends | Usually weak | Complementary retrieval layer |
| Letta/MemGPT | Agent-managed persistent memory/runtime | High | Increasingly | Implementation-specific | Can consume or generate OAK artifacts |
| Mem0 | Extract/consolidate/retrieve durable memory | High | Backend-oriented | Some | Competes with manual maintenance, not interchange semantics |
| Zep/Graphiti | Temporal knowledge graph | High | Lower | Strong | Heavy alternative for graph-centric applications |
| A-MEM | Agent-created evolving memory network | High | Moderate | Emergent | Strong Bitter-Lesson alternative |
| LangGraph store | Runtime persistence/state | Application-defined | Low–moderate | Application-defined | Storage/runtime layer |
| AGENTS.md / CLAUDE.md | Agent instructions/context | Low | **High** | Minimal | Adjacent but must remain authority-separated |
| MCP resources | Context/resource interoperability | N/A | N/A | Transport-level | Distribution layer for OAK, not replacement |
| ADRs | Durable decisions | Manual | **High** | Status/supersession | Strong structural predecessor |
| Event sourcing | Historical state reconstruction | Systematic | Moderate | **Strong events** | Supports record/history reasoning |
| Bitemporal DB | Multiple time dimensions | Systematic | Low | **Very strong** | Source for temporal semantics |
| W3C PROV / JSON-LD | Formal provenance/linked data | Structured | Moderate | **Very strong** | Source of ideas; too heavyweight for core |
| Plain Markdown prose | Human/agent notes | Manual | **Maximum** | Implicit | OAK’s true baseline |

This makes OAK’s plausible niche unusually precise:

**OAK is the layer between unstructured Markdown and a full memory/database system: enough semantics to preserve meaning across time and tools, but not enough machinery to dictate memory architecture.**

If OAK cannot demonstrate value in that narrow niche, it probably should not exist.

## The Bitter Lesson and what survives better models

Sutton’s Bitter Lesson predicts trouble for any OAK feature whose value comes mainly from making today’s models reason more reliably. As models improve, manually engineered interpretive scaffolding tends to become less valuable relative to general methods that exploit more compute. citeturn567627search1

There are two possible readings.

The **strong anti-OAK reading** is that increasingly capable agents will infer note type, currentness, relationships, contradictions, and task relevance directly from prose. They will search huge corpora, automatically construct graphs, reconcile conflicts, summarize records, and update memories. Long-context capacity is already expanding, and systems such as A-MEM, Mem0, Graphiti, and Letta show increasing automation of memory organization. Under this future, hand-maintained `kind`, folder taxonomy, generic links, indexes, and workflow instructions become tax on humans and agents. citeturn146060search9turn263677academia9turn263677academia8turn263677search0turn263677search6

The **pro-OAK reading** is that computation cannot infer information that was never preserved. If a note says “database is PostgreSQL,” no amount of future reasoning proves whether that statement describes an event in 2024, the current system, an abandoned plan, a mistaken inference, or an instruction—unless surrounding evidence remains accessible. Explicit provenance and temporal facts increase the information available to the model. This is compatible with the Bitter Lesson because the model remains free to perform all reasoning itself.

A useful field-design test is therefore:

> **Could a highly capable future agent recover this fact reliably from the artifact and its surrounding repository without the field?**

Applied to v0.3:

| Field / concept | Future agent can often infer? | Information can be irretrievably lost? | Recommendation |
|---|---:|---:|---|
| `kind` | Often | Sometimes | Keep, but validate whether three values are useful |
| `status` | Sometimes | **Yes** | Keep for mutable references/specs |
| `at` | Rarely if absent | **Yes** | Strong core field |
| `as_of` | Rarely if absent | **Yes** | Strong core field, clarify semantics |
| `sources` | Sometimes | **Yes** | Strong core field |
| `superseded_by` | Sometimes | **Yes** | Strong core lifecycle relation |
| `origin` | Sometimes | **Yes** | Keep concept, redesign semantics |
| generic `links` | Usually | Less often | Remove from core; ordinary Markdown links suffice |
| folder taxonomy | Usually | No | Guidance, not standard |
| `index.md` | Usually | No | Optional profile/tooling convention |
| daily journal | N/A | No | Workflow guidance only |
| self-check procedure | N/A | No | Tooling/conformance profile, not knowledge semantics |
| typed relations | Often inferable | Occasionally | Extension, not core |
| claim-level provenance | Often not recoverable | **Yes** | Optional advanced profile |
| stable identifier | Filename often sufficient locally | **Yes after rename/export** | Add as optional core / required interchange profile |
| uncertainty/confidence | Often ambiguous | **Yes** | Support minimally; avoid numeric fake precision |
| authority | Dangerous to infer | **Yes** | Preserve source actor, but **do not turn OAK into authority mechanism** |

The fields most likely to survive five years of model progress are therefore **time, source, identity, lifecycle transition, human/agent attribution, revocation, and explicit uncertainty**. The least likely are navigational structures and hand-authored retrieval hints.

Three future scenarios follow.

**In the next one to two years**, memory frameworks will likely continue combining large contexts with selective retrieval, consolidation, and background maintenance. The strongest argument for OAK will be portability between those systems and transparent human inspection, not raw recall performance. This is an inference from current product and research trajectories, not a measured forecast. citeturn263677search6turn263677academia8turn567627academia10turn146060search9

**Over three to five years, a high-capability scenario** would make most note classification, indexing, linking, conflict detection, and maintenance automatic. OAK survives only if it is sufficiently small that automated agents can emit it cheaply and sufficiently semantic that those annotations remain useful across implementations. This is the scenario in which a rich v0.4 ontology would age badly.

**Over three to five years, a fragmented-agent scenario** could make OAK more valuable. Different models, local agents, hosted services, human collaborators, and MCP-accessible resources may all need to share durable state. The more heterogeneous the runtime layer becomes, the more useful a vendor-neutral artifact convention can become. MCP’s rapid development as a cross-tool resource protocol illustrates the broader demand for interoperability, though MCP itself does not imply that OAK will succeed. citeturn263677search4

The condition under which OAK becomes redundant is clear: if agents can reliably preserve provenance, time, state transitions, deletion intent, and source attribution automatically in ubiquitous underlying stores—and interchange those semantics across vendors—then OAK adds little. That possibility should be treated as a valid success/failure criterion, not resisted.

## Does metadata actually beat prose?

This is the most important unresolved empirical question.

The current Papercut result does not answer it because OAK appears to bundle several interventions: structured metadata, explanatory rules, file organization, indexing, and maintenance behavior. If OAK uses fewer turns or tool calls, the cause might be `kind`; it might be `index.md`; it might be shorter prose; it might be explicit reading instructions; or it might simply be the fact that somebody curated the knowledge more carefully.

That distinction matters because **a prose convention may dominate a metadata standard** if the benefits mostly come from maintenance discipline.

The strongest existing evidence in adjacent systems actually supports testing this possibility seriously. AGENTS.md intentionally uses ordinary Markdown without required fields. Claude Code likewise relies heavily on prose instruction files. Modern models can extract structure from natural language, while memory frameworks increasingly create structure dynamically. citeturn567627search8turn263677search5turn263677academia9

A decisive OAK evaluation should therefore use a factorial design rather than “OAK versus control”:

| Condition | Equivalent information | Structured metadata | Maintenance guide | Explicit index |
|---|---:|---:|---:|---:|
| Plain | Yes | No | No | No |
| Prose semantics | Yes | No | Yes | No |
| Metadata-only | Yes | Yes | No | No |
| Indexed prose | Yes | No | Yes | Yes |
| Full OAK | Yes | Yes | Yes | Yes |

The prose condition must contain **exactly the same semantic information** as the metadata condition. For example:

`as_of: 2026-11-01`

must be compared with natural language such as:

“Verified against the running system on November 1, 2026.”

Otherwise the experiment tests added information, not structured syntax.

The hypotheses should be preregistered:

**H1 — semantic preservation:** explicit temporal/provenance metadata reduces stale or wrongly attributed actions relative to equally informative prose.

**H2 — parse efficiency:** metadata reduces tokens, tool calls, or turns required to locate current knowledge.

**H3 — maintenance reliability:** agents update structured metadata more reliably than equivalent prose after state changes.

**H4 — structure cost:** metadata increases authoring/maintenance burden and schema errors.

**H5 — intelligence interaction:** metadata advantage shrinks as model capability increases.

**H6 — heterogeneity advantage:** metadata advantage increases when multiple models/tools alternately maintain the same repository.

The current Papercut study has several threats to validity. Near-ceiling accuracy makes incremental differences difficult to detect. A 0.3-percentage-point observed difference provides little practical evidence unless the cost of an error is enormous. A total of 120 runs may sound large, but effective power depends on the number of independent repositories/tasks, per-case variance, model variance, and whether runs sharing cases/prompts are treated as independent. Tool-call and turn reductions are encouraging but can arise from navigation differences rather than memory semantics. LLM judges may introduce correlated measurement error unless calibrated against human or deterministic labels. A single repository cannot demonstrate portability across knowledge domains.

The planned 10–15-session longitudinal study is directionally much better because OAK’s strongest claim concerns **maintenance over time**. It should, however, deliberately inject state changes rather than wait passively for them: decisions reversed, preferences changed, tasks completed, facts invalidated, conflicting updates introduced, paths renamed, records corrected, one fact deleted, and two agents editing concurrently.

The experimental unit should be a **complete longitudinal trajectory**, not an individual question within a trajectory. Results should be analyzed hierarchically across trajectory, model, task class, and memory condition. Otherwise repeated questions over the same evolving repository can create pseudoreplication.

A strong primary endpoint is:

> **stale-action rate: proportion of tasks in which the agent acts on information that was no longer valid at the decision point.**

Secondary endpoints should include incorrect provenance attribution, failure to notice conflict, repeated completed work, failure to honor deletion, maintenance omissions, broken references, tool calls, turns, input tokens, wall-clock cost, and human/agent editing effort.

A reasonable preregistered promotion threshold would be something like: OAK must reduce stale-action failures by **at least 20% relative or 5 percentage points absolute**, with a confidence interval excluding zero across heterogeneous trajectories, while increasing total maintenance effort by no more than roughly 15%. Those thresholds are proposed product criteria, not empirically established constants.

Security should be a separate experiment rather than hidden inside the memory-quality benchmark. 2026 memory-poisoning research makes this important enough to test directly. Compare plain Markdown, OAK with R1, and host-enforced untrusted-memory handling under planted malicious content across sessions. Expectation: metadata alone should **not** be claimed as a defense unless experiments demonstrate it. citeturn879756academia0turn879756academia1turn879756academia3

A deletion experiment should similarly follow a write–use–delete–probe sequence and test both explicit records and derived references. Recent memory-security work increasingly evaluates complete lifecycle behavior rather than merely whether a memory row disappeared, which is the right model for OAK too. citeturn879756academia1turn146060search28

## Proposed v0.4 RFC

The v0.4 normative core should be noticeably smaller than the v0.3 document even if the overall publication includes additional non-normative guidance.

### Core semantic model

I recommend retaining the three kinds provisionally:

```text
record
    A durable account of an event, observation, or assertion in context.
    Records are historical evidence and SHOULD NOT be rewritten merely
    because later knowledge differs.

reference
    A maintained representation of what is currently believed or known
    for some purpose.

spec
    A maintained representation of a desired or intended state.
```

The key change is to remove examples such as “plan” from the semantic definition and emphasize **descriptive role rather than file genre**.

The current rule “when a file mixes kinds, choose the kind that fits most of it” should become weaker. Mixed-kind documents are precisely where future readers can misinterpret historical statements as current claims.

Proposed wording:

```diff
- When a file mixes kinds, choose the kind that fits most of it.
- Split it only if the mix confuses readers.

+ A resource SHOULD have one dominant semantic role.
+ If statements with materially different temporal or authority semantics
+ would be ambiguous when interpreted under one kind, they SHOULD be
+ separated or explicitly labeled in the body.
```

### Temporal semantics

`at` and `as_of` are worth preserving, but their definitions need sharper separation.

```diff
  at
- Records only. When the event happened, not when the file was written.
+ For records, the time at which the described event or observation
+ occurred, when known. `at` is event time, not file creation time.

  as_of
- References and specs only. When the content was last checked as true.
+ For maintained resources, the time at which the maintainer last had
+ evidence supporting the resource's maintained state.
+ `as_of` is epistemic/verification time. It MUST NOT be interpreted as
+ the time at which every statement in the resource became valid.
```

Do **not** add full `valid_from`, `valid_to`, `observed_at`, `recorded_at`, and `transaction_time` to the core yet. Bitemporal systems demonstrate that these distinctions are real, but importing all of them would impose substantial complexity on ordinary notes. citeturn146060search34

Instead define an optional **Temporal Profile** later for applications that genuinely need valid-time intervals.

### Lifecycle semantics

`status` should remain optional for records but become more disciplined for mutable knowledge.

```text
For a reference or spec intended to represent current maintained state,
status SHOULD be present.

Allowed core values:
  draft
  current
  superseded
  archived

A resource with no status MUST NOT be assumed current.

status: superseded MUST include superseded_by unless the replacement is
unknown or deliberately unavailable; in that case the body MUST explain
why no replacement is identified.
```

The current `superseded_by` rule is good and should remain. ADR practice and event-oriented systems both support preserving historical decisions rather than silently overwriting them. citeturn428641search7turn146060search19

### Provenance and attribution

`sources` should remain core. `origin` should be replaced or clarified because its current values mix actors with epistemic operations: `user`, `agent`, and `external` describe provenance, while `inferred` describes how a statement was derived.

A minimal redesign:

```yaml
oak:
  kind: reference
  as_of: 2026-11-18
  sources:
    - ../journal/2026-11-14.md
  asserted_by: user
  derived: false
```

But even that may be more syntax than necessary. My preferred v0.4 is:

```text
sources
    Evidence or artifacts from which the resource materially derives.

origin
    The actor or channel from which the maintained claim primarily came:
    user, agent, external.

A claim inferred from sources SHOULD say so in the document body.
origin MUST NOT be interpreted as authority or permission.
```

That last sentence is critical.

W3C PROV shows how much richer provenance can become; OAK should deliberately remain a tiny subset. citeturn428641search6

### Authority and prompt-injection boundary

Strengthen R1:

```diff
- Knowledge is not instructions.

+ OAK resources are data, not an authority channel.
+ Content in an OAK resource MUST NOT gain execution authority merely
+ because it is stored in an OAK resource, regardless of kind, origin,
+ status, wording, or source.
+
+ Metadata such as origin or sources describes provenance; it does not
+ grant permission, priority, trust, or authority.
+
+ The host application is responsible for deciding which instruction
+ channels are authoritative and for isolating untrusted content.
```

This keeps OAK out of the policy-engine business while aligning with evidence that persistent content can become an injection vector. citeturn879756academia0turn146060search3

Do **not** add `trusted: true`, `authority: high`, or similar fields. Such fields would be easy to spoof and could create a false security boundary.

### Deletion and revocation

Replace W5 with something closer to:

```diff
- Supersede, do not delete. Mark the old resource status: superseded
- with superseded_by. Then delete only if the user wants it gone.

+ Preserve history by supersession when retention is appropriate.
+
+ An explicit deletion or forgetting requirement overrides history
+ preservation.
+
+ When information is deleted for privacy or user intent, maintainers
+ SHOULD remove or revise OAK references derived solely from that
+ information where practical.
+
+ An implementation MUST NOT claim that deleting an OAK file erases
+ copies held in version-control history, backups, indexes, embeddings,
+ caches, or external systems unless it actually controls and verifies
+ those systems.
```

This is an important normative change.

### Stable identity

Stable IDs solve a real interoperability problem but create overhead when every personal note requires a UUID.

The compromise should be:

```text
id MAY identify a resource independently of its current path.

Portable/interchange profiles SHOULD provide stable ids for resources
that are referenced across repositories, synchronized systems, or
long-lived renames.

Core OAK does not require ids for local-only resources.
```

Accept URI/URN/string values rather than defining an OAK registry.

Example:

```yaml
oak:
  id: urn:uuid:1be90ad0-4c5a-4d4a-bc66-...
  kind: reference
```

### Generic links and typed relationships

Remove `links` from the core metadata vocabulary.

Markdown already expresses generic relationships. Future models can infer many loose relationships from prose, and `links` currently provides little semantics beyond “related.” If typed relationships prove valuable experimentally, introduce an extension:

```yaml
oak:
  relations:
    - type: depends_on
      target: urn:uuid:...
```

But **do not standardize relation names in v0.4**. This is a classic ontology-expansion trap.

### Conflict and uncertainty

Avoid a numeric `confidence: 0.72` field. Agent-generated probabilities are often false precision unless calibrated.

Add only:

```text
A maintained resource with a known unresolved material conflict SHOULD
make that conflict explicit in the body.

A resource MUST NOT mark itself current merely by choosing one conflicting
claim unless the maintainer has evidence resolving the conflict.
```

Optionally permit:

```yaml
oak:
  state: disputed
```

but I would first test whether `status` plus prose is sufficient.

### Folder layout, index, setup, and maintenance

These are useful but should become a **Recommended Files Profile**, not core conformance.

The v0.3 requirement that every resource be reachable from `index.md` within one additional file is an optimization for present-day browsing, not enduring semantics. Modern retrieval systems, filesystem search, embeddings, graph indices, and long context can all navigate repositories differently. The strongest Bitter-Lesson move is not to standardize navigation.

Similarly, instructions to create `AGENTS.md`, `CLAUDE.md`, particular folders, one daily journal, and end-of-session procedures should be non-normative recipes. AGENTS.md and Claude Code are relevant current ecosystems, but a vendor-neutral knowledge standard should not normatively depend on particular instruction-file products. citeturn567627search8turn263677search5

### Conformance model

Define three levels:

```text
OAK Core Resource
  Markdown resource containing an oak block with a recognized kind.
  Core fields obey their defined semantics.

OAK Knowledge Set
  A collection of Core Resources whose internal OAK references resolve
  or explicitly indicate an unavailable external target.

OAK Managed Profile
  A Knowledge Set that additionally follows maintenance checks such as
  status validation, supersession resolution, provenance checks, and
  optional indexing.
```

This separation makes a file portable without requiring the entire workflow.

A validator should test syntax and invariants only:

```text
kind is recognized
dates parse
status value is recognized
superseded => superseded_by exists or explicit unresolved marker
local source targets resolve
id is unique within the knowledge set when supplied
fields unknown to validator are preserved
```

It should **not** claim to validate truth, freshness, authority, or security.

### Backward compatibility

v0.3 documents should remain valid v0.4 Core Resources.

Migration should require no rewrite except for newly invalid combinations. `origin: inferred` should remain accepted as a deprecated legacy value. `links` should remain readable but become non-core. Existing `index.md` files and folder layouts remain valid Managed Profile conventions. `at`, `as_of`, `sources`, `status`, and `superseded_by` retain their names.

That makes v0.4 evolutionary rather than disruptive.

## Decision criteria, roadmap, and strongest case against OAK

The strongest case against OAK is straightforward:

**Good agents already understand Markdown, and poor memory maintenance is an agency/runtime problem rather than a serialization problem.** If agents fail to update stale files, adding YAML does not fix the responsible process. Future systems may automatically infer entities, timelines, contradictions, salience, and relationships better than humans or static schemas. Every required field introduces authoring cost, schema drift, incomplete metadata, and opportunities for false confidence. AGENTS.md’s deliberately schema-free adoption model and A-MEM’s dynamically generated organization both point toward “less standard, more intelligence.” citeturn567627search8turn263677academia9

That argument should be included prominently in the RFC. A standard that cannot state its own falsification condition is too easy to rationalize indefinitely.

The adoption argument on the other side should therefore avoid claims about intelligence. Tool builders will care if OAK gives them **portable information their systems otherwise lose**:

a source-neutral way to know “this is historical, not current,” “this was checked on this date,” “this replaced that,” “this came from the user rather than an inferred summary,” and “this item has been revoked.”

Developers will care if the format requires virtually no infrastructure and remains readable in Git diffs.

End users will care if memory is inspectable, editable, portable between agents, and capable of preserving the distinction between what they actually said and what an agent inferred.

Those incentives are much stronger than “better YAML for AI.”

An evidence matrix for the program is:

| Proposition | Current evidence | Confidence |
|---|---|---|
| Long-term agents struggle with updating and temporal reasoning | LongMemEval, LoCoMo | **Established** citeturn428641search1turn428641search2 |
| Very large context removes the need for memory organization | Contradicted by long-context evaluation | **Low** citeturn428641search3turn428641search4 |
| Persistent memory introduces security risks | Multiple 2026 benchmarks/studies | **Established enough to design for** citeturn879756academia0turn879756academia1turn879756academia3 |
| Temporal/provenance distinctions are useful information models | Longstanding DB/PROV practice | **Established conceptually** citeturn146060search34turn428641search6 |
| OAK metadata improves agent accuracy vs equivalent prose | Papercut does not show meaningful improvement | **Unproven** |
| OAK reduces navigation/tool cost | Papercut signal only | **Weak/promising** |
| OAK improves longitudinal freshness | Not yet tested convincingly | **Unproven** |
| Three kinds are the optimal taxonomy | No direct evidence | **Speculative** |
| `index.md` is necessary for modern agents | No direct evidence | **Speculative** |
| Stable identity improves multi-tool interchange | Strong engineering rationale, little OAK-specific evidence | **Likely** |
| Claim-level provenance is worth its maintenance cost | No OAK evidence | **Unknown** |
| Rich typed relationships improve outcomes | Graph-memory systems suggest possible value | **System-dependent** citeturn567627academia10turn263677academia9 |
| Better models will eliminate need for explicit temporal/provenance facts | Cannot recover absent information | **Unlikely in absolute form** |
| Better models will eliminate much manual organization | Current trajectory supports possibility | **Plausible** citeturn263677academia8turn263677academia9turn263677search6 |

The ranked roadmap should therefore be:

1. **v0.4 semantic cleanup.** Narrow the scope; clarify time, provenance, deletion, authority, and lifecycle; demote layout/workflow to profiles.
2. **Factorial metadata-vs-prose experiment.** Determine whether syntax contributes independent value.
3. **Longitudinal mutation benchmark.** Multiple repositories, models, writers, reversals, completion events, conflicts, deletions, and renames.
4. **Security/deletion lifecycle suite.** Explicitly test poisoned memory and forgetting rather than claiming R1 is protective.
5. **Reference validator.** Tiny CLI/library validating syntax and local invariants; no database.
6. **Two independent integrations.** Ideally one file-centric coding agent and one runtime-memory system consuming/emitting OAK.
7. **Only then evaluate stable IDs and a provenance profile.**
8. **Defer graph relations and claim-level provenance until measured demand exists.**

There should be two possible product paths after those experiments.

The **conservative path** is preferred: OAK remains a 1–2 page semantic convention with roughly six meaningful fields, plus optional profiles and examples. Its success metric is portability and reduction in stale/ambiguous durable knowledge.

The **ambitious path** should be triggered only by evidence: stable IDs, claim-level provenance, relation typing, conflict objects, temporal intervals, and machine-readable interchange could become extension specifications. W3C PROV and JSON-LD provide mature concepts if this becomes necessary, but OAK should adopt them by mapping rather than reimplementing them. citeturn428641search6turn428641search5

Promotion beyond **Experimental** should require preregistered evidence rather than time or enthusiasm. A reasonable bar would be all of the following: replicated reduction in stale-action or attribution errors on heterogeneous longitudinal tasks; no material harm relative to equally informative prose on strong models; demonstrated interoperability across at least three independent implementations or agent environments; successful migration of v0.3 artifacts; validation tooling; and a security statement verified against adversarial-memory tests.

If those experiments instead show that **maintenance guidance alone captures almost all the benefit**, OAK should shrink further into a best-practices document.

If equally informative prose performs as well while being easier to maintain, **structured metadata should become optional**.

If increasingly capable models automatically maintain provenance and temporal state reliably across heterogeneous tools, **OAK should be sunset rather than expanded**.

That willingness to disappear is important. The Bitter Lesson does not imply that explicit data should never be structured; it implies that human-designed structure should earn its long-term place by supplying information computation cannot cheaply rediscover. citeturn567627search1

The durable thesis for OAK v0.4 is therefore much narrower than “agent memory needs a standard”:

> **Agents will become much better at reading, searching, organizing, and maintaining knowledge. They will not become able to reconstruct provenance, event time, verification time, lifecycle transitions, or revocation that nobody preserved. OAK should standardize those irrecoverable facts—and almost nothing else.**

That is the version of OAK most likely to remain useful if the models get dramatically better.
