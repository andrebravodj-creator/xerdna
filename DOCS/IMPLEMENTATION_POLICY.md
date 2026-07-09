# IMPLEMENTATION POLICY

**Prepared by:** the independent XERDNA Scientific Architecture Review Board.
**Status:** Governance policy, not implementation, not code. This document defines how implementation — code, schemas, infrastructure (MASTER_CONTEXT.md Article I, Level 6) — may occur from Phase 2 onward, on the baseline frozen in `DOCS/PHASE_001_FREEZE.md`. It elaborates MASTER_CONTEXT.md Article XII stages 8–10 (Implementation, Validation, Release) for operational use, the same way Article IV elaborates Article IX and Article XII elaborates Article IX for the pipeline as a whole. It does not itself map onto a single named stage in Article XII's ten-stage list — Article XII names *what* Implementation, Validation, and Release must accomplish; this document names *how*, the same relationship Article IV already has to Article IX. This gap is noted rather than silently smoothed over, consistent with this Board's practice throughout.

**Binding scope:** every line of code, every schema (database, not conceptual), every API, every ingestion connector, every AI/reasoning component, and every interface built in XERDNA from this point forward is governed by this policy. No implementation is exempt by virtue of being "small," "temporary," or "just a prototype" — MASTER_CONTEXT.md Article II Rule 5 draws no such exception, and neither does this document.

---

## 1. Implementation Principles

1. **No implementation without a traced design.** Nothing is built without an existing Level-5 design document (or an amendment to one) that itself traces to a ratified constitutional article (Article I, Article II Rule 5). "We'll document it after" is not permitted — Scientific Constitution Before Code means the document precedes the code, not follows it.
2. **No implementation without an Approval.** Per Article XII stage 7, implementation may only begin against a design that has passed Architecture → Review → Decision → Audit → Remediation → Approval, with an `APPROVED` decision on record for that specific scope. Phase 1's `DOCS/PHASE_001_FREEZE.md` is the first instance of this; every subsequent phase, and every significant expansion within a phase, needs its own.
3. **Extension over replacement, by default.** New implementation extends existing structures (new entity types, new connectors, new endpoints) rather than replacing them, per Article IV — replacement is permitted only when explicitly justified in the governing design document, not chosen for implementation convenience.
4. **No silent scope expansion.** If implementation work reveals a need beyond what was approved, that need goes back through the pipeline (at minimum, a new Decision-stage entry, e.g. in a `DATA/`-local decisions log mirroring GRAPH/SCHEMA_DECISIONS.md's structure) before it is built — it does not get added quietly inside an unrelated change.
5. **Reversibility is chosen by default.** Where two implementation approaches solve a problem equally well, the more reversible one is chosen (Article V Rule 5), and the choice is recorded when it wasn't obvious.

## 2. Documentation Requirements

1. Every implemented component (a service, a connector, an API surface, a reasoning module) has an implementation note stating: which design document and which specific finding/decision ID (e.g. `GRAPH/SCHEMA_DECISIONS.md E1`) it satisfies; what, if anything, was deliberately deferred or simplified relative to the design; and its own version.
2. Deviations from the approved design are recorded with a stated rationale at the point of deviation, in the same why/impact/risk shape GRAPH/SCHEMA_DECISIONS.md already uses — not discovered later by diffing code against docs.
3. Every `DATA/` ingestion connector's design document must include the per-source evidence-tiering rubric required by GRAPH/SCHEMA.md's E1 rule *before* the connector is authorized to run — this is a documentation requirement with a hard implementation gate attached, not a suggestion.

## 3. Architectural Traceability

1. Every implemented unit (function, table/collection, endpoint, pipeline stage) must be traceable through the full chain: **implementation → design document → constitutional article** (Level 6 → Level 5 → Levels 1–3, per Article I). A reviewer must be able to answer "why does this exist" by walking that chain without guessing.
2. A traceability manifest is maintained per implemented component (a structured comment block, a manifest file, or equivalent — the mechanism is an implementation detail, the requirement is not): listing the design document section(s) and constitutional article(s) it implements. This extends the "Serves:" citation pattern GRAPH/SCHEMA.md already uses at the document level, down to the implementation level.
3. Every one of GRAPH/SCHEMA.md's `Rule:` statements that is meant to be mechanically enforced (not merely descriptive) must have an identifiable implementation location responsible for enforcing it — untraceable enforcement (a rule that's supposed to be automatic but no code owns it) is treated as a gap, not an oversight to fix later.

## 4. Review Requirements

1. No implementer approves their own work's constitutional compliance. Review is independent — a different person, or a different Board-style pass, checks the implementation against the design document and the Non-Negotiable Rules before merge.
2. Review explicitly checks two separate things, not conflated into one pass: **correctness** (does it do what the design says) and **constitutional compliance** (does it preserve the evidence-tier separation, provenance mandatoriness, and Anti-Hallucination Rules at runtime, not just in the code's intent).
3. Any review finding that a Non-Negotiable Rule (Article II) is at risk of being violated blocks merge unconditionally — this is not a severity-graded finding subject to DEFER, the way an entity-coverage gap can be. Article II Rule 5 is not negotiable at the implementation layer any more than at the design layer.

## 5. Validation Requirements

1. Corresponds to Article XII stage 9. Before release, every implementation is validated against two things: that it behaviorally matches the design document it claims to implement, and that every constitutional constraint the design document states is actually enforced, not merely documented.
2. Validation produces a record — a validation report, checklist, or equivalent artifact — the same way Audit and Approval stages produce documents. "Tests passed" is not itself a validation record; what was validated, against which design, with what result, is.
3. At minimum, validation must demonstrate: an untiered record is rejected at the system boundary (Article II Rule 1, enforced); a record missing `primary_knowledge_source` or `source_record_id` is rejected (Design Rule 2); a `computational_prediction` cannot silently become `established_evidence` without an independent established-evidence record (Prediction Model rule); no query path can return graph data without its `evidence_tier` and `primary_knowledge_source` (Scientific Integrity Constraint 2).

## 6. Testing Requirements

1. Every `Rule:` statement in GRAPH/SCHEMA.md (and any future phase's equivalent design document) that is meant to be enforced in running code has at least one corresponding automated test asserting that enforcement — the tests are the executable form of the schema's own stated rules, not a separate, independently-derived test suite.
2. The eight Anti-Hallucination Rules are treated as a standing regression suite requirement for any AI/reasoning component: no entity without a resolvable origin, no relationship without a source span, no `established_evidence` from generative inference, no unresolved citation treated as weak-but-present, no fuzzy identity merging, no invented confidence, inspectable reasoning, re-derivable output — each is testable, and each must be tested, not merely asserted in a design document.
3. Tests covering evidence-tier boundary rejection, provenance-field mandatoriness, and the Checked-Absent Records exemption (that a `checked_absent` record is correctly *not* required to carry a tier, and correctly *not* treated as an association) are required before any component that writes either kind of record is released.

## 7. Scientific Verification Requirements

1. **Never invent scientific metadata.** Any ontology version, database release, publication identifier, or scientific standard an implementation depends on is verified from its authoritative source before it is hardcoded, configured, or committed — the same standard already applied in freezing GRAPH/SCHEMA.md's Pinned Vocabulary Versions and Term-Level Verification sections. This is a standing rule for this project, not a one-time practice.
2. Where a term or version cannot be verified, the implementation states the gap explicitly (an `ontology_gap: true`-style flag, an "unpinned" note, or equivalent) rather than substituting a plausible-looking value — mirroring how ChEBI and SO were left honestly unpinned rather than guessed, and how `biolink:InformationResource` was flagged rather than silently replaced.
3. No `DATA/` ingestion connector is authorized against an ontology or database release that has not been verified, at the time the connector is built — a prior verification (even one performed for GRAPH/SCHEMA.md itself) does not carry forward indefinitely; ontologies and databases continue to release after this document is written.
4. Scientific accuracy takes precedence over speed, unconditionally. A slower, verified implementation is preferred over a faster, unverified one at every decision point this policy governs.

## 8. Rollback Policy

1. Every implementation change has a defined rollback path *before* it is deployed, not designed retroactively after a failure — consistent with Article V Rule 5 (reversibility as a design criterion) and Decision Principle 3 (Article VII).
2. Rollback must preserve provenance and evidence-tier integrity. Rolling back a bad ingestion never leaves orphaned untiered records, silently deletes established-evidence provenance, or breaks a hypothesis's chain back to the evidence that resolved it — a rollback is itself a traceable, recorded operation, not a raw deletion.
3. Rollback of an entity that has since been split or merged (R2, GRAPH/SCHEMA.md Entity Identity) respects the same lineage discipline the schema defines for splits/merges — it does not silently collapse or discard the lineage record to make the rollback simpler.
4. If a rollback would require violating any Non-Negotiable Rule (Article II) to execute, the rollback is redesigned, not the rule.

## 9. Versioning Policy

1. Every implemented service, connector, or API carries its own version, explicitly tied to the `schema_version` (R1) and design-document version(s) it was built against — extending the constitutional Amendment Log / Schema Changelog discipline down to the implementation layer.
2. A compatibility record (a matrix, manifest, or equivalent) maps implementation versions to the `schema_version` range they support. This is what makes GRAPH/SCHEMA.md's `schema_version` field on every node and edge actually useful at query time — without a compatibility record, the field is metadata nobody consumes.
3. Version increments follow the same discipline already established constitutionally: not incremented casually, and every increment recorded with what changed and why — the same shape as MASTER_CONTEXT.md's Amendment Log and GRAPH/SCHEMA.md's Schema Changelog, applied one layer down.

## 10. Deprecation Policy

1. Nothing implemented is ever silently removed. Deprecation is a recorded state transition (`status: active | deprecated`, extended to cover implementation components the same way it already covers `xerdna:` namespace entries and predicates per B4), not a deletion.
2. A deprecated component remains queryable and auditable for provenance purposes after being superseded — consistent with the Provenance Model's `status` field (E3) and VISION.md Article V Rule 3 (refutation and history are signal, not noise, at the data layer; the same principle extends to the systems that produced the data).
3. Every deprecation names its replacement, or states explicitly that there is none yet and why the component is being retired regardless — recorded with the same rationale discipline as every other governance artifact in this chain.

---

## How This Policy Guarantees Constitutional Compliance

Each section above is traceable to what it prevents, made explicit here rather than left implicit:

| Policy section | Constitutional guarantee it enforces |
|---|---|
| 1. Implementation Principles | Article I (nothing below Level 5 outranks it); Article II Rule 5 (Scientific Constitution Before Code) |
| 2. Documentation Requirements | Article III Rule 3 (visible reasoning for a future reader); GRAPH/SCHEMA.md's E1 rubric requirement |
| 3. Architectural Traceability | Article I's full hierarchy, made checkable at the implementation layer, not just the design layer |
| 4. Review Requirements | Article II Rule 5 (Non-Negotiable Rules aren't negotiable at merge time either) |
| 5. Validation Requirements | Article XII stage 9; VISION.md Article IV (tiers must actually hold at runtime, not just on paper) |
| 6. Testing Requirements | The Anti-Hallucination Rules and every `Rule:` in GRAPH/SCHEMA.md, made mechanically enforced, not just documented |
| 7. Scientific Verification Requirements | The standing "never invent scientific metadata" rule; Anti-Hallucination Rule 4 |
| 8. Rollback Policy | Article V Rule 5 (reversibility); R2 (split/merge lineage, extended to operational failure recovery) |
| 9. Versioning Policy | R1 (`schema_version`), made load-bearing rather than decorative |
| 10. Deprecation Policy | E3 (provenance lifecycle status) and VISION.md Article V Rule 3, extended from data to systems |

No implementation may proceed under this policy while any row above is unmet for the component in question — this is the mechanism by which "no future implementation can violate the constitutional architecture" is guaranteed: not by trusting intent, but by requiring each guarantee to have a named, checkable enforcement point before release.
