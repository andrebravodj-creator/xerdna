# PHASE 002 REMEDIATION PLAN

**Status:** Governance record, not implementation. This document does not modify DOCS/PHASE_002_DESIGN.md or any other document. It plans corrections; it does not apply them. Per the governance pipeline (MASTER_CONTEXT.md Article XII), this is the Remediation-stage output (stage 6) for the 15 ACCEPT NOW findings in [DOCS/PHASE_002_DECISIONS.md](PHASE_002_DECISIONS.md), triaged from [DOCS/PHASE_002_REVIEW.md](PHASE_002_REVIEW.md). No code is written here. Per explicit instruction, this Board stops after this document and waits for approval before editing PHASE_002_DESIGN.md.

**Scope:** all 15 ACCEPT NOW findings. The 1 DEFER finding (TG3, this review process's limited independence) has no design-document correction to plan — see PHASE_002_DECISIONS.md's own entry for it — and is not repeated here.

**Documents affected:** every finding below resolves entirely within `DOCS/PHASE_002_DESIGN.md` — no other document (GRAPH/SCHEMA.md, MASTER_CONTEXT.md, IMPLEMENTATION_POLICY.md, etc.) requires any change to close any of these 15 items. This is noted once here and stated per-finding below only for completeness against the requested field set.

---

## 1. BLOCKING REMEDIATIONS

These 7 findings must be resolved before Implementation (Article XII stage 8) may begin — an implementer following the design as it currently stands could not produce something that actually satisfies GRAPH/SCHEMA.md's rules or IMPLEMENTATION_POLICY.md's guarantees without these fixes.

### WVS1 — Section 6 fields missing from Sections 4–5's canonical structure

- **Problem:** `source_span`, `resolution_status`, and `basis` are described in Section 6 (Anti-Hallucination Rule Enforcement Matrix) as real, required fields, but none appear in Section 4's storage tables (`associations`, `confidence`) or Section 5's gate-check lists. The design's own sections disagree about what the schema contains.
- **Constitutional impact:** Undermines MASTER_CONTEXT.md Article V Rule 1 (typed, never ad hoc) at the design-document level itself — a field the document claims is enforced but never structurally defines is functionally ad hoc, regardless of intent.
- **Scientific impact:** `resolution_status` and `basis` are direct mechanisms protecting against unverified-but-plausible claims (VISION.md Article VIII); an implementation missing them silently loses the protection the design claims to provide.
- **Engineering impact:** Without this fix, an implementer working from Section 4/5 alone builds a schema that cannot deliver Section 6's claims — a rebuild would be needed once the gap is discovered, most expensively during Validation.
- **Smallest possible correction:** Add `source_span` to `associations`; add `resolution_status` to `associations` (or a citation sub-table, if citations are modeled separately); add `basis` to `confidence`. Three field additions to two existing tables — no new tables, no restructuring.
- **Dependency order:** No dependency on any other finding. Must be applied **before** SI2 (which reuses the `source_span` pattern) and should be applied before TG2 (manifest completeness) is finalized.
- **Risk:** Low to apply now, before any code exists. High to defer — an implementation built on the inconsistent version would need revision after the fact.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Sections 4, 5).

### MEP1 — Hypothesis Model's established-evidence mechanism unmodeled

- **Problem:** GRAPH/SCHEMA.md states a hypothesis `status` transition to `refuted`/`supported_by_experiment` is itself an `established_evidence` event — a second pathway to that tier, distinct from the Prediction Model's `promoted_from` link. The design only models the prediction pathway, and `promoted_from`'s type is unrestricted as to which tier it may reference.
- **Constitutional impact:** Risks blurring the tier-separation VISION.md Article VIII treats as load-bearing at every surface, by leaving two structurally distinct "become established_evidence" events representable through one ambiguous mechanism.
- **Scientific impact:** Conflates two different scientific events — an experiment validating a hypothesis, versus an independent citation confirming a model's prediction — which carry different provenance chains and different epistemic weight.
- **Engineering impact:** As designed, there is no correct way to represent a resolved hypothesis in storage, and nothing prevents `promoted_from` from being misused to link a hypothesis to an established_evidence record via the wrong mechanism.
- **Smallest possible correction:** Add a second resolution mechanism (a hypothesis `status` transition to `supported_by_experiment`/`refuted` requires insertion of its own linked `established_evidence` record, referenced from the `hypotheses` table, not via `promoted_from`); restrict `promoted_from` (Section 4.3) to only reference `computational_prediction`-tier `associations`.
- **Dependency order:** No dependency on any other finding. Independent of WVS1, but thematically adjacent (both restructure Section 4) — efficient to apply in the same editing pass as WVS1, immediately after it.
- **Risk:** Low to apply now, before any hypothesis-tier records exist. High to defer — retrofitting a second resolution pathway after hypotheses have already been resolved via the wrong mechanism would require re-auditing every such record's provenance chain.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Sections 4.3, 4.5, 5).

### SI2 — `source_asserts_causation` self-certifying

- **Problem:** The flag enforcing E2 (never default to a causal predicate without source support) is a bare boolean with no evidentiary backing — trivially satisfiable by anyone authoring a row, defeating the rule's purpose in substance while appearing to satisfy it in form.
- **Constitutional impact:** A gate that only appears to enforce VISION.md Article VIII's central concern (tier/claim-strength blurring) without actually doing so is arguably a subtler violation than having no gate at all, since it creates false confidence in a design review that doesn't look closely.
- **Scientific impact:** Reintroduces, one layer down, the exact correlation-to-causation strengthening risk E2 exists to prevent — the predicate is correctly gated, but the gate's own input requires no proof.
- **Engineering impact:** An implementer following the design as written builds a gate that passes review but does not actually enforce E2 in substance — a defect likely to go unnoticed without a dedicated test (see MEP2 in Non-Blocking, below, which should also verify this specific strengthening once applied).
- **Smallest possible correction:** Replace the boolean `source_asserts_causation` with a required source-passage reference field, reusing the `source_span` pattern once WVS1 adds it — the gate then checks for presence of a real reference, not merely a true/false value.
- **Dependency order:** Depends on WVS1 (reuses its `source_span` field pattern). Apply immediately after WVS1.
- **Risk:** Low to apply now; high to defer, since retrofitting an evidentiary requirement onto a boolean-only field after real predicate data exists means re-auditing every prior `causes` insertion.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Sections 4.3, 5.2, 6 row 2/E2).

### WVS3 — SQLite pragma/trigger specifics unstated

- **Problem:** SQLite disables foreign-key enforcement by default per connection; the design's referential-integrity claims (`node_xrefs`, `associations` subject/object, `entity_lineage`) silently depend on `PRAGMA foreign_keys = ON` being set, which the design never states. Separately, Section 5.3's "row-level constraint" language for immutability doesn't specify that this requires a `BEFORE UPDATE` trigger (a `CHECK` constraint cannot compare old/new values across an update).
- **Constitutional impact:** Risks an implementation that appears to satisfy MASTER_CONTEXT.md Article V Rule 2 (provenance is mandatory, not optional) while silently not enforcing it at the storage layer at all.
- **Scientific impact:** Nearly every scientific guarantee this design makes depends on referential integrity actually holding — an unenforced foreign key means an xref, an association endpoint, or a lineage record could point at nothing, silently corrupting exactly the traceability VISION.md Article V Rule 4 requires.
- **Engineering impact:** A well-known SQLite trap; an implementer could plausibly build this prototype without ever discovering the gap, since the schema would look correct on inspection and only a deliberate "insert an orphaned reference" test would catch it.
- **Smallest possible correction:** State explicitly, in Section 3 or a new Section 5.4, that `PRAGMA foreign_keys = ON` is set on every connection, and that immutability (Section 5.3) is implemented specifically via `BEFORE UPDATE` triggers, not `CHECK` constraints.
- **Dependency order:** No dependency on any other finding. Should be applied **before** MEP4, which extends the same trigger-based immutability mechanism this finding clarifies.
- **Risk:** Low to apply now; high to defer, since this class of gap is not caught by casual testing.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Sections 3, 5.3).

### MEP4 — `schema_version` immutability unstated

- **Problem:** `evidence_tier` and `xerdna_id` are explicitly called out as immutable post-insert (Section 4.1); `schema_version` is not, despite R1's entire purpose depending on the same guarantee.
- **Constitutional impact:** Undermines VISION.md Article IX ("Build for 2,000 phases") at the exact point GRAPH/SCHEMA_DECISIONS.md R1 identified as the clearest instance of that principle's failure mode — a field that costs nothing to protect now and becomes unrecoverable once records exist without the protection.
- **Scientific impact:** `schema_version` lets future reasoning correctly interpret a record's field set relative to what schema version it was created under; a mutable value breaks that interpretive guarantee silently.
- **Engineering impact:** Building the immutability trigger for only the two fields the design names, rather than all three that need it, is a natural and easy-to-miss omission for an implementer following the design faithfully.
- **Smallest possible correction:** Add `schema_version` to the immutability guarantee already specified in Section 4.1, enforced via the same two-layer mechanism (application + `BEFORE UPDATE` trigger, per WVS3) already specified for `evidence_tier`/`xerdna_id`.
- **Dependency order:** Depends on WVS3 (reuses the trigger-mechanism clarification it provides). Apply immediately after WVS3.
- **Risk:** Low to apply now, before any schema_version mutation has occurred; the omission is cheap to close precisely because nothing has been implemented yet.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Sections 4.1, 5.3).

### MEP3 — `status` value set unvalidated

- **Problem:** `status` is specified as "required, defaults to active" with no stated constraint on other acceptable values — as written, any string would be accepted, defeating E3's bounded lifecycle (`active` / `retracted` / `superseded_by:<id>`).
- **Constitutional impact:** Undermines MASTER_CONTEXT.md Article IV (provenance and traceability prioritized over convenience) and the E3 rule specifically, which GRAPH/SCHEMA_REVIEW.md originally rated `Critical`.
- **Scientific impact:** An unbounded `status` field can silently accumulate meaningless or contradictory values, undermining the retraction/supersession tracking E3 exists to enable — and the defect would not surface until a much later phase tries to consume the field and finds it unreliable.
- **Engineering impact:** Straightforward to add a value-set constraint; the risk is entirely in *not* adding it before real status transitions occur.
- **Smallest possible correction:** Add an explicit constraint to Section 4.1/4.3 and Section 5.1: `status` must be one of the three valid forms, with `superseded_by:<id>` validated against an existing record ID at insert time.
- **Dependency order:** No dependency on any other finding. Fully self-contained; can be applied at any point in the blocking sequence.
- **Risk:** Low to apply now; high to defer, since an already-inconsistent field is far harder to clean up retroactively than to constrain from the start.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Sections 4.1, 4.3, 5.1).

### TG1 — No target code directory specified

- **Problem:** MASTER_CONTEXT.md Article IX names specific folders with specific purposes, but the design never commits this prototype's eventual code to one of them.
- **Constitutional impact:** Leaves a MASTER_CONTEXT.md Article VI/IX naming-convention question unresolved at the design stage, which the constitution's own discipline treats as a design-document responsibility, not an implementer's ad hoc choice.
- **Scientific impact:** None directly — a structural/organizational matter.
- **Engineering impact:** Code cannot be written without a location to write it in; leaving this undecided means the first implementer makes an unrecorded structural decision.
- **Smallest possible correction:** Add one sentence stating implementation code will live in `GRAPH/engine/` (extending the folder MASTER_CONTEXT.md Article IX already assigns to "the biological knowledge graph itself"), with the one-line rationale already given in PHASE_002_REVIEW.md's recommendation (extend, don't invent, per Article V Rule 3).
- **Dependency order:** No dependency on any other finding. Fully independent — can be applied first, as a prerequisite settled before any schema-level fix, or at any other point in the sequence.
- **Risk:** Negligible either way, but costs nothing to close immediately.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (a new or extended line in Section 3 or a new Section).

---

## 2. NON-BLOCKING REMEDIATIONS

These 8 findings are accepted but do not prevent Implementation from beginning once the 7 blocking items above are resolved. They should still be applied — per Scientific Constitution Before Code, an ACCEPT NOW finding left permanently unapplied is not meaningfully different from one that was never accepted — but they may be closed during design polish, the Testing/Validation stage, or (in WVS2's case) inherited by a later Roadmap phase, without holding up the start of coding.

### CC1 — VISION.md Article VII not addressed

- **Problem:** The design's Constitutional basis line never cites Article VII (Ethical Principles), leaving its non-applicability implicit rather than stated.
- **Constitutional impact:** Minor traceability gap against MASTER_CONTEXT.md Article II Rule 6 (ethics and biosecurity are absolute) — the omission is very likely benign given the prototype's scope, but is unstated.
- **Scientific impact:** None.
- **Engineering impact:** None — no code path is affected.
- **Smallest possible correction:** One sentence stating Article VII was considered and found non-applicable (no individual-level clinical/genomic data, no dual-use design capability in this prototype's scope).
- **Dependency order:** None. Fully independent.
- **Risk:** Negligible.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Constitutional basis line or a new short subsection).

### SI1 — Allow-list presented as standing in for E1's rubric

- **Problem:** The `established_evidence` source allow-list (Section 5.2) is described as standing in for E1's per-source tiering rubric without stating this is a scope simplification specific to this prototype.
- **Constitutional impact:** Risks a future `DATA/` connector citing this prototype as precedent for skipping E1's actual, finer-grained rubric requirement.
- **Scientific impact:** Protects the Evidence Model's `established_evidence` gate from being satisfied by a coarser instrument than the constitution requires, for any future work that might look to this prototype as a model.
- **Engineering impact:** None to this prototype's own code — the mechanism is sound for its own scope.
- **Smallest possible correction:** One caveat sentence in Section 5.2 stating the allow-list is valid only for this prototype's hand-authored seed data and sets no precedent for real ingestion connectors.
- **Dependency order:** None. Should ideally precede MEP2 (which adds a test proving the allow-list's rejection path), so the test is written against the caveated, correctly-scoped version of the rule — but this is a soft ordering preference, not a hard dependency.
- **Risk:** Low to apply now; moderate to defer, growing with time as more design work might reference this prototype.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Section 5.2).

### SI3 — `infores:` CURIE convention unspecified

- **Problem:** `primary_knowledge_source`/`aggregator_knowledge_source` value format is unstated, risking inconsistent source-naming across seed data.
- **Constitutional impact:** Risks quietly reintroducing the ambiguity the B2 fix (GRAPH/SCHEMA.md v1.2) specifically closed around how knowledge sources are represented.
- **Scientific impact:** Low direct impact, but consistency of source identifiers is a precondition for any future cross-record source analysis.
- **Engineering impact:** None to gate logic — an implementer familiar with GRAPH/SCHEMA.md's own examples would likely infer the convention correctly regardless.
- **Smallest possible correction:** One note added to Section 4.1/4.3's field descriptions stating these fields follow the `infores:` CURIE convention.
- **Dependency order:** None. Fully independent.
- **Risk:** Negligible.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Sections 4.1, 4.3).

### WVS4 — Python version unpinned

- **Problem:** Section 3 specifies "Python 3" generically, not a minimum version.
- **Constitutional impact:** Minor inconsistency with this project's own established version-pinning discipline (O1), applied to ontologies but not yet to this prototype's own runtime.
- **Scientific impact:** None.
- **Engineering impact:** Low — an unpinned minimum version could, in principle, allow a build against a Python version lacking a language feature the implementation assumes.
- **Smallest possible correction:** State a minimum version explicitly (e.g., "Python ≥ 3.10") in Section 3.
- **Dependency order:** None. Fully independent.
- **Risk:** Negligible.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Section 3).

### MEP2 — No test for allow-list rejection path

- **Problem:** The allow-list mechanism (Section 5.2) is specified but never proven by a test or seed case.
- **Constitutional impact:** IMPLEMENTATION_POLICY.md Section 6 requires every enforced rule to have a corresponding test; this one currently doesn't.
- **Scientific impact:** An untested gate is asserted, not demonstrated — weaker than every other tier-boundary rule in the design, which does have a corresponding test.
- **Engineering impact:** Low — adds one test case; does not change any gate logic.
- **Smallest possible correction:** Add one seed/test case: an `established_evidence` insert attempted against a source not on the allow-list, expected to be rejected (mirroring T8's structure for the `causes`-without-support rejection).
- **Dependency order:** Best applied after SI1 (so the test is written against the caveated, correctly-scoped allow-list) and after SI2 (if the same test pattern is reused for the strengthened causation-evidence check). Not a hard blocking dependency.
- **Risk:** Low either way — the underlying mechanism is not believed broken, only unproven.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Sections 7, 8).

### MEP5 — T15 has no corresponding seed data

- **Problem:** T15 (Namespace Registry enforcement) has no seed data in Section 7 that clearly exercises it — none of the seed entities/predicates are `xerdna:`-namespaced except, implicitly and unstated, the split/merge seed row.
- **Constitutional impact:** IMPLEMENTATION_POLICY.md Section 6's testing requirement is nominally satisfied (a test ID exists) but not substantively (unclear what it runs against).
- **Scientific impact:** None directly — a Namespace Registry testing-completeness matter, not an evidence-tier one.
- **Engineering impact:** Low — either a documentation clarification or one small added seed case.
- **Smallest possible correction:** State explicitly in Section 7 or 8 that T15 is exercised via the `entity_lineage` seed row's use of `xerdna:split_into`/`xerdna:merged_from`, or add a standalone case if that connection is judged too indirect.
- **Dependency order:** Best applied after the blocking Section 4/5 fixes (WVS1, MEP1) are finalized, so it references stable field names. Not a hard dependency.
- **Risk:** Low either way.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Sections 7, 8).

### WVS2 — Read-path enforcement weak

- **Problem:** The guarantee that reads always surface `evidence_tier` and `primary_knowledge_source` (Section 2, T14) rests on a single, unenforced function, unlike every write-path guarantee, which has defense-in-depth.
- **Constitutional impact:** This prototype's own single read function can satisfy GRAPH/SCHEMA.md's Scientific Integrity Constraint 2 today; the risk is forward-looking, to whichever future phase adds a second read path.
- **Scientific impact:** Protects the visibility of evidence tiers at every future query surface, per VISION.md Article VII Rule 5 (honesty about what the system is).
- **Engineering impact:** None to this prototype's own required functionality; the fix is a design note establishing a pattern for future extension, not a change to what must be built now.
- **Smallest possible correction:** Add a design note describing a single canonical query layer that always joins tier and source, with no lower-level accessor exposed that could bypass it — a pattern for later phases to extend rather than reinvent.
- **Dependency order:** None. Fully independent; can be applied at any point.
- **Risk:** Low to apply (a note costs nothing); the residual risk this doesn't fully close is that a future phase might still bypass the pattern despite the note.
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Section 2 or a new subsection).

### TG2 — Traceability manifest incomplete

- **Problem:** Section 10's manifest names 6 components against 9 storage tables and 16 tested rules — substantially under-representing what the design actually builds.
- **Constitutional impact:** IMPLEMENTATION_POLICY.md Section 3 (Architectural Traceability) is only partially satisfied by the current manifest.
- **Scientific impact:** None directly.
- **Engineering impact:** None to code; a documentation-completeness matter useful to future auditors.
- **Smallest possible correction:** Extend Section 10 to cover the Hypothesis Model, Confidence Model, and Anti-Hallucination Rule enforcement points currently missing.
- **Dependency order:** Must be applied **last**, after WVS1, MEP1, and SI2 are applied — otherwise the manifest would need a second pass to reflect the corrected field set.
- **Risk:** Negligible, but doing this before the blocking fixes land would waste the effort (the manifest would immediately go stale).
- **Documents affected:** DOCS/PHASE_002_DESIGN.md only (Section 10).

---

## 3. Recommended Application Order

A single sequence spanning both groups, since some non-blocking items have soft or hard dependencies on blocking ones. Numbers in brackets indicate hard dependencies (must follow); unbracketed items have no hard dependency and are placed for narrative/editing efficiency only.

| Order | Finding | Group | Depends on |
|---|---|---|---|
| 1 | TG1 — target code directory | Blocking | None |
| 2 | WVS1 — Section 6 fields → Sections 4–5 | Blocking | None |
| 3 | MEP1 — Hypothesis Model resolution mechanism | Blocking | None (grouped with WVS1 for editing efficiency) |
| 4 | SI2 — `source_asserts_causation` strengthened | Blocking | **[2]** WVS1 |
| 5 | WVS3 — SQLite pragma/trigger mechanism stated | Blocking | None |
| 6 | MEP4 — `schema_version` immutability | Blocking | **[5]** WVS3 |
| 7 | MEP3 — `status` value set validated | Blocking | None |
| 8 | CC1 — Article VII note | Non-blocking | None |
| 9 | SI1 — allow-list caveat | Non-blocking | None |
| 10 | SI3 — `infores:` convention note | Non-blocking | None |
| 11 | WVS4 — Python version pinned | Non-blocking | None |
| 12 | WVS2 — read-path design note | Non-blocking | None |
| 13 | MEP2 — allow-list rejection test | Non-blocking | soft: **[9]** SI1 |
| 14 | MEP5 — T15 seed-data connection | Non-blocking | soft: **[2,3]** WVS1, MEP1 |
| 15 | TG2 — traceability manifest completed | Non-blocking | **[2,3,4]** WVS1, MEP1, SI2 |

**Why this order is safest:** the two structural fixes (WVS1, MEP1) land first because three other items (SI2, and soft dependencies for MEP5 and TG2) build on them — applying them first avoids editing the same sections twice. WVS3 precedes MEP4 for the same reason, at smaller scale. TG1 is placed first among equals because it is a zero-dependency prerequisite question best settled before any schema editing begins, even though nothing else technically requires it first. The five fully independent non-blocking items (CC1, SI1, SI3, WVS4, WVS2) are ordered arbitrarily among themselves — none affects any other. TG2 is last by hard requirement, since it summarizes the state everything else leaves behind.

---

## What Happens Next

No document has been modified by this plan. Per explicit instruction, this Board stops here and waits for approval before editing DOCS/PHASE_002_DESIGN.md. Once authorized, the 15 corrections above should be applied in the order given in Section 3, each as an explicit, individually traceable edit — the same discipline GRAPH/SCHEMA_DECISIONS.md's ACCEPT NOW items were held to when applied to GRAPH/SCHEMA.md.
