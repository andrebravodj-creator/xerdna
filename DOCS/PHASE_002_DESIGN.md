# PHASE 002 DESIGN — Universal Biological Memory Engine (Prototype)

**Constitutional basis:** this document is a Level-5 Architecture-stage artifact (MASTER_CONTEXT.md Article I, Article XII stage 2). It implements [ROADMAP.md](../ROADMAP.md) Article II ("Phase 1 — Universal Biological Memory" in the Roadmap's own numbering — see the naming note immediately below), under [VISION.md](../VISION.md) Article IV, V, VI, VIII, IX, and [MASTER_CONTEXT.md](../MASTER_CONTEXT.md) Article II, IV, V, and the newly-ratified Article XII. It is the first implementation-facing design document XERDNA has ever produced, and is governed by [DOCS/IMPLEMENTATION_POLICY.md](IMPLEMENTATION_POLICY.md) once code exists, and by the baseline frozen in [DOCS/PHASE_001_FREEZE.md](PHASE_001_FREEZE.md) at every point before that.

**On VISION.md Article VII (Ethical Principles):** considered and found non-applicable to this prototype's scope — it contains no individual-level clinical or genomic data and no dual-use biological design capability (Section 7's seed data is limited to generic Gene/Protein/Disease entity types with no patient- or agent-level content). Stated explicitly rather than left silent. *(CC1, PHASE_002_DECISIONS.md)*

**A naming note, stated explicitly to avoid the ambiguity this project has caught elsewhere:** "Phase 002" here refers to this repository's own *work-phase* numbering (Phase 001 = constitutional and architectural freeze; Phase 002 = first implementation) — it is not ROADMAP.md's phase numbering. What this document designs implements ROADMAP.md **Article II**, which the Roadmap itself calls "**Phase 1** — Universal Biological Memory." These are two different numbering systems for two different things (this repo's engineering milestones vs. the Roadmap's mission sequencing) and are not interchangeable — the same category of distinction this project drew between Article X's reading order and Article I's precedence order.

**Status:** Architecture only. No code has been written. This document is not self-authorizing — per MASTER_CONTEXT.md Article XII, it must pass Review → Decision → Audit → Remediation → Approval before Implementation (stage 8) may begin, the same discipline Phase 001's GRAPH/SCHEMA.md was held to. See "Next Steps," at the end.

**Design version:** 1.2 — see Design Changelog, below. Version 1.2 closes the three implementation-blocking issues found in the final engineering readiness review of v1.1.

---

## 1. Objective

Build the smallest possible local-only software system that proves GRAPH/SCHEMA.md's rules can be *mechanically enforced*, not merely documented. This is a proof of enforcement, not a product, not an ingestion pipeline, and not a research tool. Its only job is to demonstrate that a record violating any of the following cannot be written to storage:

- missing or invalid `evidence_tier`
- missing provenance (`primary_knowledge_source`, `source_record_id`)
- missing `schema_version`
- missing source identifiers (xrefs, for nodes; `source_record_id`, for provenance)
- any of the eight Anti-Hallucination Rules, to the extent each is mechanically checkable without network access (see Section 6)
- a direct, silent rewrite of `evidence_tier` from `computational_prediction` to `established_evidence`
- any record — of any kind, including a `checked_absent` record — entering storage without the scientific metadata its own tier/kind requires

## 2. Scope

### In scope

- A single local, file-based data store. No server process, no network listener, no multi-user access.
- A minimal insertion API that every write must pass through — the "gate" described in Section 5.
- A minimal read API that always surfaces `evidence_tier` and `primary_knowledge_source` alongside any data returned (Scientific Integrity Constraint 2, GRAPH/SCHEMA.md) — implemented as a **single canonical query layer** that always joins tier and source, with no lower-level accessor exposed that could bypass it. This prototype has only one read path today, but the pattern is stated now so any future read path (most likely Phase 2/3, Roadmap numbering, building a reasoning engine on top of this storage layer) extends it rather than inventing a second, unenforced one. *(WVS2, PHASE_002_DECISIONS.md)*
- A small, hand-authored seed set (not a real ingestion connector) — enough entities and associations to exercise every rule in Section 1 at least once, not a realistic-sized dataset.
- A test suite proving each rule in Section 1 is actually enforced, not just intended (IMPLEMENTATION_POLICY.md Section 6).

### Explicitly out of scope, and why

| Excluded | Why |
|---|---|
| Frontend, UI, visualization | Explicit instruction; also, Phase 4 (Biological Simulator) territory, not Phase 1/2. |
| Public app, HTTP server, authentication | Explicit instruction; "local-only" means a local process invoked directly, not a service. |
| AI agent, reasoning, hypothesis generation | Explicit instruction; also Phase 2/3 (Roadmap numbering) territory — this prototype only proves the storage/enforcement layer Phase 2/3 will eventually write *into*. |
| Production infrastructure (deployment, scaling, monitoring, backups-as-a-service) | Explicit instruction; a local prototype has no production posture to speak of. |
| Real ingestion connectors (UniProt, PubMed, ClinicalTrials.gov, etc.) | `DATA/`'s own future work, per GRAPH/SCHEMA.md's "What This Document Is Not." Only hand-authored seed records are used here. |
| Full Biolink category coverage | GRAPH/SCHEMA.md's Biological Entity Types table names ~19 categories; this prototype implements the generic node/association machinery those categories are instances of, and seeds only 3 (Section 7) — enough to exercise every rule without building out the full catalog. |
| External citation resolution (DOI/PMID lookups against a live registry) | Requires network access, which conflicts with "local-only." Anti-Hallucination Rule 4's *field requirement* is enforced (Section 6); its *resolution mechanism* is deferred to whichever `DATA/` connector first needs it, and is never faked in the meantime (see Section 6, Rule 4). |
| Graph traversal, reasoning, gap-finding | ROADMAP.md Article III (Phase 2, Roadmap numbering) — a later phase's work, building on top of what this prototype proves. |

## 3. Technology Choice

**SQLite, accessed from Python 3's standard-library `sqlite3` module. No other runtime dependency.**

Justified against MASTER_CONTEXT.md Article IV / Article V Rule 4 ("boring, well-understood foundations... over anything clever that is hard to migrate away from"):

- Single file, zero server process, trivially "local-only" — deleting the file resets the entire prototype.
- Enforces constraints (`NOT NULL`, `CHECK`, foreign keys, triggers) at the storage boundary itself, not only in application code — a second, independent enforcement layer beneath the API gate (Section 5), consistent with IMPLEMENTATION_POLICY.md Section 5's validation discipline (behavioral match *and* runtime-enforced constraints, not just code that's supposed to check).
- Ubiquitous, extensively understood, in every mainstream language's standard toolchain — the definition of "boring" this project has committed to for every load-bearing choice so far (Biolink/OBO for vocabulary; SQLite for the first storage layer).
- Reversible: GRAPH/SCHEMA.md's own "What This Document Is Not" section already defers the *production* graph storage engine (property graph vs. RDF triple store vs. hybrid) as a separate `DATA/`-level decision. SQLite here is explicitly a prototype-only choice, not a claim about what Phase 1's eventual production backend will be — migrating away from it later costs nothing this design depends on (Article V Rule 5, reversibility).

Python is chosen for the same reason: it ships `sqlite3` in its standard library (zero extra dependency surface for a prototype whose entire point is to be small and inspectable), and is broadly legible to any future contributor per VISION.md Article IX's "people not yet in the room."

**Enforcement mechanics, stated explicitly:** SQLite disables foreign-key enforcement by default per connection — `PRAGMA foreign_keys = ON` is set on **every** connection this engine opens, with no code path that opens a connection without it. Every referential-integrity claim in Section 4 (`node_xrefs`, `associations` subject/object, `entity_lineage`, `hypotheses.resolved_by`) depends on this being enabled and is otherwise silently unenforced. Immutability (Section 5.3) is implemented via **`BEFORE UPDATE` triggers**, specifically — not `CHECK` constraints, which cannot compare a row's old and new values across an update. *(WVS3, PHASE_002_DECISIONS.md)*

**Minimum version:** Python ≥ 3.10, stated explicitly rather than left generic, consistent with this project's version-pinning discipline (O1) applied so far to scientific vocabularies and now extended to this prototype's own runtime. *(WVS4, PHASE_002_DECISIONS.md)*

### Code Location

Implementation code lives in **`GRAPH/engine/`** — extending the folder MASTER_CONTEXT.md Article IX already assigns to "the biological knowledge graph itself," rather than introducing a new top-level folder for a single prototype (Article V Rule 3, extend over invent). *(TG1, PHASE_002_DECISIONS.md)*

## 4. Storage Structure (Conceptual — Not DDL)

Described at the field level, the same way GRAPH/SCHEMA.md itself is written — not as runnable SQL, consistent with "do not write code yet."

### 4.1 `nodes`

| Field | Constraint | Serves |
|---|---|---|
| `xerdna_id` | Primary key; namespaced (`xerdna:gene:001`, etc.) | Entity Identity |
| `category` | Required; a Biolink/OBO/`xerdna:` type string | Design Rule 1 (typed, never ad hoc) |
| `evidence_tier` | Required; one of the three literal tier values, no other value accepted | Evidence Model |
| `primary_knowledge_source` | Required; follows the `infores:` CURIE convention (e.g. `infores:uniprot`), matching GRAPH/SCHEMA.md's Provenance Model examples and its v1.2 correction on how knowledge sources are represented *(SI3, PHASE_002_DECISIONS.md)* | Provenance Model |
| `aggregator_knowledge_source` | Optional; same `infores:` convention | Provenance Model |
| `retrieved_at` | Required | Provenance Model |
| `source_record_id` | Required | Provenance Model |
| `status` | Required; defaults to `active`; **must be one of `active` / `retracted` / `superseded_by:<id>`, no other value accepted; a `superseded_by:<id>` value is validated against an existing record ID at insert time** | Provenance Model (E3) *(MEP3, PHASE_002_DECISIONS.md)* |
| `schema_version` | Required; the GRAPH/SCHEMA.md version this record was created under; immutable post-insert (see below) | Schema Versioning (R1) |

Once inserted, `evidence_tier`, `xerdna_id`, and `schema_version` are immutable — no update path exists for any of the three, at either the API layer or the storage layer (Section 5.3), enforced via the same `BEFORE UPDATE` trigger mechanism (Section 3). `schema_version` is included because R1's entire purpose — letting a future reader distinguish "valid under an earlier schema" from "malformed" — depends on the field never changing after the fact. *(MEP4, PHASE_002_DECISIONS.md)*

### 4.2 `node_xrefs`

| Field | Constraint | Serves |
|---|---|---|
| `xerdna_id` | Foreign key to `nodes` | Entity Identity |
| `namespace` | Required (e.g. `HGNC`, `NCBIGene`) | Entity Identity |
| `external_id` | Required | Entity Identity |

A node with zero rows here must instead carry an explicit, logged rationale (a `no_xref_rationale` field on `nodes`, populated only when `node_xrefs` is empty) — enforcing Anti-Hallucination Rule 1 (no entity without a resolvable origin *or* an explicit, logged rationale for minting one with none).

### 4.3 `associations`

| Field | Constraint | Serves |
|---|---|---|
| `id` | Primary key | — |
| `subject_id`, `object_id` | Foreign keys to `nodes` | Relationship Types |
| `predicate` | Required | Relationship Types |
| `qualifier` | Optional | O4 (predicate-plus-qualifier) |
| `evidence_tier` | Required; same three-value enum as `nodes` | Evidence Model |
| `primary_knowledge_source`, `source_record_id`, `retrieved_at`, `status`, `schema_version` | Required, same rules as `nodes` — including `status`'s three-value constraint and `schema_version`'s immutability *(MEP3, MEP4, PHASE_002_DECISIONS.md)* | Provenance Model, R1 |
| `promoted_from` | Optional foreign key to another `associations.id`; **must reference a `computational_prediction`-tier association only** — never a `research_hypothesis`-tier one, which resolves via the separate mechanism in Section 4.5 | Prediction Model promotion rule (Section 5.3); Hypothesis Model resolution, kept distinct *(MEP1, PHASE_002_DECISIONS.md)* |
| `source_span` | Required on any row whose `primary_knowledge_source` indicates literature extraction (vs. structured database ingestion, where the source record itself is the span) | Anti-Hallucination Rule 2 *(WVS1, PHASE_002_DECISIONS.md)* |
| `resolution_status` | Required; one of `resolved` / `unresolved` / `not_checked`; defaults to `not_checked`; nothing in this prototype ever sets it to `resolved`, since resolution requires network access out of scope for "local-only" (Section 2) | Anti-Hallucination Rule 4 *(WVS1, PHASE_002_DECISIONS.md)* |

**Rule enforced here, not just documented:** a `correlated_with`-shaped finding (a statistical association) may never be inserted with predicate `causes` unless `source_span` is populated with the source's own specific passage asserting causation — mirroring E2 exactly (Section 6 restates this as a testable rule). *(Strengthened per SI2, PHASE_002_DECISIONS.md — see below; a bare boolean flag was replaced with this evidentiary requirement, reusing the `source_span` field above.)*

### 4.4 `confidence`

| Field | Constraint | Serves |
|---|---|---|
| `association_id` | Foreign key | Confidence Model |
| `confidence_type` | Required only if the parent association's `evidence_tier` is `computational_prediction` or `research_hypothesis`; forbidden (must be absent) if `established_evidence` | Confidence Model |
| `value` | Required alongside `confidence_type` | Confidence Model |
| `basis` | Required when `confidence_type` is `qualitative`; an explicit textual justification — never a synthesized number standing in for a missing natural score | Anti-Hallucination Rule 6 *(WVS1, PHASE_002_DECISIONS.md)* |

The "forbidden if `established_evidence`" half of this rule is enforced at the storage layer, not left to application discipline (Section 5.3) — this is the concrete mechanism preventing "established facts come in degrees of trust," per GRAPH/SCHEMA.md's own stated rationale for the rule.

### 4.5 `hypotheses`

| Field | Constraint | Serves |
|---|---|---|
| `association_id` | Foreign key; the parent record's `evidence_tier` must be `research_hypothesis` | Hypothesis Model |
| `claim` | Required; may reference multiple `nodes`/`associations` (a subgraph), per H2 | Hypothesis Model |
| `supporting_evidence` | Required (may be an empty, explicit list) | Hypothesis Model |
| `contradicting_evidence` | Required; if empty, `none_found_as_of` must carry a date — never silently blank | Hypothesis Model |
| `reasoning` | Required | Hypothesis Model, VISION.md Article VI Rule 4 |
| `status` | One of `open` / `under_investigation` / `refuted` / `supported_by_experiment`; changeable, never terminal (H4) | Hypothesis Model |
| `generated_by` | Required | Hypothesis Model |
| `resolved_by` | Required only when `status` transitions to `refuted` or `supported_by_experiment`; foreign key to a new, separately-inserted `established_evidence`-tier `associations` row recording the experiment's finding — **not** the same mechanism as `promoted_from` (Section 4.3), which is reserved for `computational_prediction` promotion only | Hypothesis Model ("`status` transitions... are themselves evidence-tier `established_evidence` events") *(MEP1, PHASE_002_DECISIONS.md)* |

**Two distinct pathways to `established_evidence`, kept structurally separate:** a `computational_prediction` becomes `established_evidence` via `promoted_from` (Section 4.3) when an independent confirming record is inserted; a `research_hypothesis` becomes resolved via `resolved_by`, when the `status` transition itself is backed by a new `established_evidence` record (an experiment's finding). Neither field may be used for the other tier's resolution — this is a scientific distinction (a hypothesis validated by experiment is a different kind of event than a prediction independently confirmed), not merely a schema convenience. *(MEP1, PHASE_002_DECISIONS.md; traceable to PHASE_002_REVIEW.md Section 3.)*

### 4.6 `predictions`

| Field | Constraint | Serves |
|---|---|---|
| `association_id` | Foreign key; parent's `evidence_tier` must be `computational_prediction` | Prediction Model |
| `method` | Required | Prediction Model |
| `method_ontology_term` | Optional | O2 |
| `ontology_gap` | Boolean; required to be `true` if `method_ontology_term` is absent | O2 |
| `model_version` | Required | Prediction Model, VISION.md Article VI Rule 3 |
| `input_reference` | Required | Prediction Model |
| `generated_at` | Required | Prediction Model |

### 4.7 `checked_absent`

| Field | Constraint | Serves |
|---|---|---|
| `subject`, `predicate`, `object` | Required | Checked-Absent Records (P1) |
| `checked_by` | Required | Checked-Absent Records |
| `checked_at` | Required | Checked-Absent Records |
| `scope` | Required | Checked-Absent Records |

**No `evidence_tier` column exists on this table, and none is added.** This is the storage-layer expression of the exemption GRAPH/SCHEMA.md now states explicitly (v1.2, Section 8 of the Checked-Absent Records rule) — the absence of the column is itself the enforcement mechanism, not an oversight.

### 4.8 `entity_lineage`

| Field | Constraint | Serves |
|---|---|---|
| `old_xerdna_id`, `new_xerdna_id` | Foreign keys to `nodes` | R2 (split/merge lineage) |
| `relation` | One of `split_into` / `merged_from` | R2 |
| `recorded_at` | Required | R2 |

A split or merge never deletes the old `xerdna_id`'s row — `status` (Section 4.1) transitions instead, and this table preserves the lineage.

### 4.9 `xerdna_namespace_registry`

| Field | Constraint | Serves |
|---|---|---|
| `prefix` | Required, unique | Namespace Registry |
| `kind` | Required; `entity_type` or `predicate` | Namespace Registry, extended scope (B4) |
| `parent_type` | Optional | Namespace Registry |
| `introduced_in` | Required | Namespace Registry |
| `rationale` | Required | Namespace Registry |
| `status` | `active` / `deprecated` | Namespace Registry, IMPLEMENTATION_POLICY.md Section 10 |

Both `xerdna:` entity-type prefixes and `xerdna:` predicates used anywhere in this prototype's seed data (Section 7) must have a row here before use — this is the mechanical closure of B4, not a documentation-only fix.

## 5. The Insertion Gate

Every write, of any kind, passes through one function-level "gate" before reaching storage — described here conceptually; the gate is not itself a database trigger, though triggers back it up as a second, independent layer (Section 5.3).

### 5.1 Universal checks (every table)

1. `schema_version` present and equal to a version this engine build declares support for (Section 9).
2. For any tiered record (`nodes`, `associations`): `evidence_tier` present and one of the three literal values; `primary_knowledge_source` and `source_record_id` present and non-empty; `status` present and one of `active` / `retracted` / `superseded_by:<id>`, with any `superseded_by:<id>` value validated against an existing record ID *(MEP3, PHASE_002_DECISIONS.md)*.
3. For `checked_absent` records specifically: the universal tier check above does **not** apply (Section 4.7) — instead, `subject`/`predicate`/`object`/`checked_by`/`checked_at`/`scope` must all be present.

### 5.2 Tier-specific checks

- `established_evidence`: no `confidence` row may be attached (rejected if attempted); source must appear, verbatim, in a small local allow-list of sources this prototype recognizes as "structured ingestion from a recognized authoritative source" (Section 7 — for a prototype with hand-authored seed data, this allow-list is itself hand-authored and tiny). **This allow-list is a scope simplification valid only because this prototype's seed data has no intra-source tier variation to speak of — it does not set precedent for any real `DATA/` ingestion connector, which must still produce a genuine per-source rubric distinguishing tiers *within* a source, per E1.** *(SI1, PHASE_002_DECISIONS.md)*
- `computational_prediction`: `predictions` row required, with `method` and `model_version` both present; `confidence` row required, with `confidence_type` stated.
- `research_hypothesis`: `hypotheses` row required, with `claim`, `contradicting_evidence` (or an explicit `none_found_as_of`), and `reasoning` all present; `confidence` row required, `confidence_type` fixed to `qualitative` (H2/Confidence Model: hypothesis confidence is never numeric at this phase).

### 5.3 The no-silent-promotion rule, enforced twice

1. **Application layer:** the gate exposes no `update_evidence_tier()`, `update_schema_version()`, or `update_xerdna_id()` function of any kind. There is no code path capable of changing a record's tier, schema version, or canonical/primary ID after insertion.
2. **Storage layer, defense in depth:** a `BEFORE UPDATE` trigger (Section 3) rejects any attempted modification of the `evidence_tier` and `schema_version` columns on both `nodes` and `associations` after insert, and of the identifying column specific to each table — `xerdna_id` on `nodes`, `id` on `associations` — independent of whether the application layer was bypassed. This means even a direct, ad hoc database edit — not just a use of the intended API — cannot silently promote a record, alter which schema version it claims to have been created under, or renumber it.
3. **Tier-restriction check, at insert time — the enforcement point for Sections 4.3 and 4.5's field constraints:** before an `associations` row with `promoted_from` populated is accepted, the gate looks up the referenced record and rejects the insert unless that record's `evidence_tier` is `computational_prediction`. Before a `hypotheses` row with `resolved_by` populated is accepted, the gate looks up the referenced record and rejects the insert unless that record's `evidence_tier` is `established_evidence`. Neither field is accepted with a reference to any other tier.
4. **The only path to a stronger tier:** for a `computational_prediction`, insert a *new* `established_evidence` record, with its own full provenance, and set that new record's `promoted_from` field to the original prediction's `id` (validated per point 3, above). For a `research_hypothesis`, insert a *new* `established_evidence` record and link it via `hypotheses.resolved_by` (Section 4.5) instead, also validated per point 3 — the two mechanisms are kept distinct, never interchanged. In both cases, the original record is never touched, deleted, or hidden — both remain independently queryable, exactly matching the Prediction Model's rule that a promotion is "linked to, not substituted for, the original prediction."

## 6. Anti-Hallucination Rule Enforcement Matrix

Each of the eight rules, and exactly how (or whether) this local-only prototype enforces it mechanically:

| # | Rule | Enforced how | Deferred? |
|---|---|---|---|
| 1 | No entity without a resolvable origin | `node_xrefs` required, or an explicit `no_xref_rationale` populated (Section 4.2) | No — fully enforced |
| 2 | No relationship without a source span | A `source_span` field is required on any `associations` row whose `primary_knowledge_source` indicates literature extraction (vs. structured database ingestion, where the source record itself is the span) | No — fully enforced for the seed data's literature-derived rows |
| 3 | `established_evidence` never from generative inference | The gate's source allow-list (Section 5.2) only accepts hand-designated "structured ingestion" sources for this tier; nothing in this prototype has a generative/LLM component at all (explicit instruction: no AI agent), so this rule is enforced by the prototype's scope, not just its code | No |
| 4 | Citations must resolve, not merely look plausible | **Partially deferred.** The *field* (`source_record_id`, and a `resolution_status` field: `resolved` / `unresolved` / `not_checked`) is required and enforced. The *resolution mechanism itself* (an actual DOI/PMID lookup) requires network access and is out of scope for "local-only" (Section 2). No record is ever allowed to claim `resolved` without an actual resolution having been performed — the gate defaults every new citation to `not_checked` and nothing sets it to `resolved` in this prototype, since nothing here performs resolution. This is the honest scope boundary: the rule is not silently skipped, its unmet half is visibly flagged on every record. |
| 5 | No silent fuzzy merging of identity | Any two nodes with overlapping xrefs are never auto-merged by this prototype; a below-threshold match is not even attempted (no similarity scoring exists in this prototype's scope) — `xerdna:possibly_same_as` insertion is a manual, explicit operation only | No |
| 6 | Confidence never invented to fill a required field | `confidence_type: qualitative` requires an explicit `basis` text field, non-empty; a `computational_prediction` whose method produces no natural numeric score must set `confidence_type: qualitative` explicitly, never a synthesized number | No — fully enforced |
| 7 | Reasoning must be inspectable | `hypotheses.reasoning` required non-empty (Section 4.5); this prototype has no reasoning *engine* generating hypotheses (Section 2), so all seed hypotheses are hand-authored with hand-written reasoning — the rule is trivially satisfiable and enforced by presence-checking, with real inspectability becoming meaningful once Phase 2/3 (Roadmap numbering) builds an actual reasoning engine on top of this storage layer | Partially — the field is enforced; genuine inspection of *generated* reasoning is a later phase's concern |
| 8 | Every generated record is re-derivable | `predictions.input_reference` and `model_version` required non-empty (Section 4.6) | No — fully enforced |

## 7. Seed Data (Illustrative, Not Ingestion)

The minimum set needed to exercise every rule above at least once, hand-authored, not sourced from any real external connector:

- **3 entity categories:** `biolink:Gene`, `biolink:Protein`, `biolink:Disease` — enough to form a subgraph-scoped hypothesis (H2) spanning three or more entities, without building out coverage for all ~19 categories GRAPH/SCHEMA.md names.
- **3 predicates:** `biolink:interacts_with` (protein–protein, `established_evidence`), `biolink:correlated_with` (gene–disease, `established_evidence`, demonstrating E2's default-to-correlation rule with a source that does *not* assert causation), `biolink:causes` (gene–disease, attempted with a source that does *not* support causation — this insertion is expected to be **rejected** by the gate, and that rejection is itself the test).
- **One `computational_prediction`** (a hand-labeled "predicted interaction," with method/model_version/confidence), later **promoted** to a new, linked `established_evidence` record — exercising the promotion rule end to end (Section 5.3).
- **One `research_hypothesis`** whose `claim` spans the Gene, Protein, and Disease seeded above (exercising H2's subgraph scope), with an explicit `none_found_as_of` for `contradicting_evidence`, **later resolved**: its `status` transitions to `supported_by_experiment`, linked via `resolved_by` to a newly-inserted `established_evidence` record — exercising the hypothesis-resolution pathway end to end, distinct from the prediction-promotion pathway exercised above.
- **One `checked_absent` record** (e.g., "checked: does Gene X correlate with Disease Y — not found, as of `<date>`, scope: hand-authored seed only").
- **One entity split** (a hand-authored `entity_lineage` row using `xerdna:split_into`), to exercise R2 without requiring a real gene-model revision — this row is also what T15 (Namespace Registry enforcement) runs against, since `xerdna:split_into` is the only `xerdna:`-namespaced term this seed set uses; it must have a corresponding `xerdna_namespace_registry` row before this insert succeeds. *(MEP5, PHASE_002_DECISIONS.md)*

## 8. Test Matrix

Per IMPLEMENTATION_POLICY.md Section 6, every enforced rule has at least one planned test, listed here at the design stage so none are silently forgotten when code is written:

| Test ID | Asserts | Covers |
|---|---|---|
| T1 | Insert with missing `evidence_tier` is rejected | Article II Rule 1, Evidence Model |
| T2 | Insert with `evidence_tier` outside the three literal values is rejected | Evidence Model |
| T3 | Insert with missing `primary_knowledge_source` or `source_record_id` is rejected | Provenance Model, Design Rule 2 |
| T4 | Insert with missing `schema_version` is rejected | R1 |
| T5 | `checked_absent` insert succeeds with no `evidence_tier` column and is not treated as an association | Checked-Absent exemption (B3) |
| T6 | Direct update of `evidence_tier` on any existing row fails, at both the application and storage layer | Section 5.3 |
| T7 | Promotion path: new linked `established_evidence` record succeeds; original `computational_prediction` remains unmodified and independently queryable | Prediction Model promotion rule |
| T8 | `causes` insertion without `source_span` populated is rejected; `correlated_with` with the same source succeeds | E2 *(field name updated per SI2, PHASE_002_DECISIONS.md)* |
| T9 | `established_evidence` insert with an attached `confidence` row is rejected | Confidence Model |
| T10 | `computational_prediction` insert missing `method` or `model_version` is rejected | Prediction Model |
| T11 | `research_hypothesis` insert missing `reasoning`, or with both `contradicting_evidence` and `none_found_as_of` empty, is rejected | Hypothesis Model |
| T12 | Node with zero `node_xrefs` and no `no_xref_rationale` is rejected | Anti-Hallucination Rule 1 |
| T13 | A citation's `resolution_status` defaults to `not_checked` and no code path in this prototype sets it to `resolved` | Anti-Hallucination Rule 4 (honest deferral) |
| T14 | Query/read functions always return `evidence_tier` and `primary_knowledge_source` alongside data — no read path can omit them | Scientific Integrity Constraint 2 |
| T15 | `xerdna:` prefix or predicate not present in `xerdna_namespace_registry` cannot be used in any insert | B4, Namespace Registry scope |
| T16 | Split/merge insert preserves both old and new `xerdna_id`; old node's `status` transitions, row is not deleted | R2 |
| T17 | `established_evidence` insert with a source not on the allow-list is rejected | E1, Section 5.2 *(MEP2, PHASE_002_DECISIONS.md)* |
| T18 | Hypothesis `status` transition to `supported_by_experiment` succeeds when `resolved_by` links to a valid `established_evidence` record; the same transition attempted with `resolved_by` empty, or pointing at a non-`established_evidence` record, is rejected | Hypothesis Model resolution, Section 4.5, Section 5.3 point 3 |

## 9. Versioning

Per IMPLEMENTATION_POLICY.md Section 9: this prototype is **Engine version 0.1.0**, declaring support for **`schema_version` 1.2 only** (GRAPH/SCHEMA.md's current frozen version, per DOCS/PHASE_001_FREEZE.md). Any record whose `schema_version` doesn't match is rejected by the gate (Section 5.1) rather than silently accepted — this prototype does not attempt multi-version compatibility; that is deferred to whichever future version actually needs it.

## 10. Traceability Manifest

Per IMPLEMENTATION_POLICY.md Section 3, the mapping this design commits its eventual implementation to:

| Storage/gate component | Design document section | Constitutional article |
|---|---|---|
| `nodes`, `associations` tier/provenance columns | GRAPH/SCHEMA.md Evidence Model, Provenance Model | MASTER_CONTEXT.md Article II Rule 1; VISION.md Article IV |
| Insertion gate (Section 5) | GRAPH/SCHEMA.md Anti-Hallucination Rules | VISION.md Article VI, VIII |
| No-update-path for `evidence_tier` (Section 5.3) | GRAPH/SCHEMA.md Prediction Model | VISION.md Article V Rule 3 |
| `checked_absent` table with no tier column | GRAPH/SCHEMA.md Checked-Absent Records, v1.2 exemption rule | VISION.md Article V Rule 5; MASTER_CONTEXT.md Article II Rule 1 (by explicit exemption) |
| `xerdna_namespace_registry`, `kind` column | GRAPH/SCHEMA.md Namespace Registry, v1.2 scope extension | MASTER_CONTEXT.md Article VI Rule 4 |
| Read API surfacing tier + source always (Section 2) | GRAPH/SCHEMA.md Scientific Integrity Constraints | VISION.md Article IV, VIII |
| `hypotheses` table, `resolved_by` field (Section 4.5) | GRAPH/SCHEMA.md Hypothesis Model resolution rule | VISION.md Article VIII; ROADMAP.md Article VII *(added per TG2, PHASE_002_DECISIONS.md)* |
| `confidence` table, tier-dependent presence and `basis` field (Section 4.4) | GRAPH/SCHEMA.md Confidence Model | VISION.md Article VIII *(TG2)* |
| `predictions` table, `method`/`model_version`/`input_reference` (Section 4.6) | GRAPH/SCHEMA.md Prediction Model | VISION.md Article V Rule 4, Article VI Rule 3 *(TG2)* |
| `associations.source_span`, `resolution_status` (Section 4.3) | GRAPH/SCHEMA.md Anti-Hallucination Rules 2, 4 | VISION.md Article VI, VIII *(TG2)* |
| `node_xrefs`, `no_xref_rationale` (Section 4.2) | GRAPH/SCHEMA.md Anti-Hallucination Rule 1; Entity Identity | MASTER_CONTEXT.md Article VI Rule 4 *(TG2)* |
| `entity_lineage` table (Section 4.8) | GRAPH/SCHEMA.md R2, split/merge lineage | VISION.md Article IX *(TG2)* |

## 11. What This Design Is Not

- **Not a production system.** No concurrency model, no auth, no deployment story — a single local file, invoked directly.
- **Not an ingestion pipeline.** Section 7's seed data is hand-authored to exercise rules, not sourced from any real database.
- **Not a reasoning engine.** Hypotheses and predictions in the seed data are hand-authored; nothing in this prototype generates them.
- **Not final on storage backend.** SQLite is this prototype's choice, not a commitment for Phase 1's eventual production graph store (GRAPH/SCHEMA.md's own "What This Document Is Not" already reserves that decision).
- **Not code.** Nothing above is runnable; Sections 4–8 describe structure and behavior, not syntax.

## Design Changelog

Distinct from GRAPH/SCHEMA.md's own Schema Changelog and from MASTER_CONTEXT.md's constitutional Amendment Log — this changelog tracks changes to this document only.

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-07-09 | Initial Architecture-stage design, ratified as the basis for Review. |
| 1.1 | 2026-07-10 | Applied all 15 ACCEPT NOW findings from [DOCS/PHASE_002_DECISIONS.md](PHASE_002_DECISIONS.md), triaged from [DOCS/PHASE_002_REVIEW.md](PHASE_002_REVIEW.md), per the order specified in [DOCS/PHASE_002_REMEDIATION.md](PHASE_002_REMEDIATION.md): target code directory named as `GRAPH/engine/` (TG1); `source_span`, `resolution_status`, and `basis` added to the canonical schema, closing the gap between Section 6's claims and Sections 4–5's structure (WVS1); a second, distinct hypothesis-resolution mechanism (`resolved_by`) added, and `promoted_from` restricted to `computational_prediction`-tier records only (MEP1); `source_asserts_causation` replaced with the evidentiary `source_span` requirement (SI2); SQLite's foreign-key pragma and `BEFORE UPDATE`-trigger mechanics stated explicitly (WVS3); `schema_version` added to the immutability guarantee (MEP4); `status`'s value set constrained and validated (MEP3); VISION.md Article VII's non-applicability stated explicitly (CC1); the allow-list caveated as a non-precedent-setting simplification (SI1); the `infores:` CURIE convention stated for source fields (SI3); a minimum Python version pinned (WVS4); a canonical read-layer design note added (WVS2); a rejection test for the allow-list added as T17 (MEP2); T15 connected to the entity-lineage seed row (MEP5); and the Traceability Manifest extended to full coverage (TG2). |
| 1.2 | 2026-07-10 | Closed the three implementation-blocking issues found in v1.1's final engineering readiness review: added seed data (Section 7) and a test, T18 (Section 8), exercising the `resolved_by` hypothesis-resolution pathway end to end, previously unexercised by anything in the design; added an explicit gate-level enforcement point (Section 5.3, new point 3) validating that `promoted_from` may only reference a `computational_prediction`-tier record and `resolved_by` may only reference an `established_evidence`-tier record, closing the gap between the field-level constraints stated in Sections 4.3/4.5 and the gate logic in Section 5; corrected Section 5.3's trigger description, which previously implied `associations` has an `xerdna_id` column — it does not, its immutable identifying column is `id`. |

## Next Steps (Not Performed Here)

Per MASTER_CONTEXT.md Article XII, this Architecture-stage document does not authorize Implementation by itself. The next stages — Review (an independent critique of this design against the constitution), Decision (triaging any findings), Audit (cross-document consistency), Remediation, and Approval — are separate, subsequent steps, each producing its own document, the same discipline Phase 001 applied to GRAPH/SCHEMA.md. Code is written only after an `APPROVED` decision is reached for this specific design.
