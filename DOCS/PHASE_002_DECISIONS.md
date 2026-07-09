# PHASE 002 DECISIONS

**Status:** Governance record, not implementation. This document is the Decision stage of the governance pipeline (MASTER_CONTEXT.md Article XII, stage 4), classifying every finding in [DOCS/PHASE_002_REVIEW.md](PHASE_002_REVIEW.md) as **ACCEPT NOW**, **DEFER**, or **REJECT**. No recommendation classified here is applied to [DOCS/PHASE_002_DESIGN.md](PHASE_002_DESIGN.md) by this document — a classification of ACCEPT NOW means "this should be incorporated into PHASE_002_DESIGN.md as an explicit, traceable edit, in a separate, subsequent Remediation step," not that it has been. Neither PHASE_002_DESIGN.md nor any implementation document is modified here, and no code is written. This is architecture governance only, mirroring the discipline GRAPH/SCHEMA_DECISIONS.md applied to GRAPH/SCHEMA_REVIEW.md.

**How to read a decision:** each finding gets *decision*, *reason* (why classified this way — not a restatement of the finding itself, which PHASE_002_REVIEW.md already gave), *constitutional justification* (the specific article grounding the call), *scientific justification* (how it bears on the Evidence Model / tier integrity specifically, distinct from general architectural soundness), *architectural impact* (what changes in the design if accepted, or what remains a known gap if not), *risk* (residual exposure either way), *dependency* (what the decision is contingent on), *whether it blocks implementation* (can code correctly satisfying the constitution be written from the design as it stands today, without this fix), *recommended implementation phase* (when this is actually addressed), and *traceability* (the exact review section/finding ID this responds to).

---

## Decision Summary

| ID | Finding | Decision | Blocks Implementation | Recommended Phase |
|---|---|---|---|---|
| CC1 | Article VII not addressed | ACCEPT NOW | No | Phase 002 (design, before Approval) |
| SI1 | Allow-list vs. rubric conflation | ACCEPT NOW | No | Phase 002 (design, before Approval) |
| SI2 | `source_asserts_causation` self-certifying | ACCEPT NOW | **Yes** | Phase 002 (design correction, before Implementation) |
| SI3 | `infores:` convention unspecified | ACCEPT NOW | No | Phase 002 (design, before Approval) |
| MEP1 | Hypothesis Model established-evidence mechanism unmodeled | ACCEPT NOW | **Yes** | Phase 002 (design correction, before Implementation) |
| MEP2 | No test for allow-list rejection | ACCEPT NOW | No | Phase 002 (Testing/Validation stage) |
| MEP3 | `status` value set unvalidated | ACCEPT NOW | **Yes** | Phase 002 (design correction, before Implementation) |
| MEP4 | `schema_version` immutability unstated | ACCEPT NOW | **Yes** | Phase 002 (design correction, before Implementation) |
| MEP5 | T15 has no seed data | ACCEPT NOW | No | Phase 002 (Testing/Validation stage) |
| WVS1 | Section 6 fields missing from Sections 4–5 | ACCEPT NOW | **Yes** | Phase 002 (design correction, before Implementation) |
| WVS2 | Read-path enforcement weak | ACCEPT NOW | No (this prototype); informs Phase 2/3 | Phase 002 (design note); Phase 2/3 Roadmap (structural fix) |
| WVS3 | SQLite pragma/trigger specifics unstated | ACCEPT NOW | **Yes** | Phase 002 (design correction, before Implementation) |
| WVS4 | Python version unpinned | ACCEPT NOW | No | Phase 002 (design, before Approval) |
| TG1 | No target code directory specified | ACCEPT NOW | **Yes** | Phase 002 (design correction, before Implementation) |
| TG2 | Traceability manifest incomplete | ACCEPT NOW | No | Phase 002 (Validation-stage documentation) |
| TG3 | Review independence limited | **DEFER** | No | Ongoing — future Review-stage practice |

**15 ACCEPT NOW, 1 DEFER, 0 REJECT.** No finding in PHASE_002_REVIEW.md was speculative, hedged, or premature process-building in the way GRAPH/SCHEMA_REVIEW.md's two REJECT items (D6, R3) were — every finding here identifies a concrete, addressable gap, so none is rejected. **7 of the 15 accepted findings block Implementation** (SI2, MEP1, MEP3, MEP4, WVS1, WVS3, TG1); the remaining 8 are accepted but non-blocking, addressed during design polish, testing, or a later Roadmap phase as noted per-item.

---

## 1. Constitutional Conflicts

### CC1 — VISION.md Article VII not addressed — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** Zero-cost to close — a single stated sentence — with a real, if small, downside if skipped: a future reader could mistake the silence for an unconsidered gap rather than a checked conclusion, exactly the ambiguity this project has repeatedly worked to eliminate elsewhere (e.g. Article X's ordering note, B1).
- **Constitutional justification:** MASTER_CONTEXT.md Article II Rule 6 (biosecurity and ethics are absolute); VISION.md Article VII.
- **Scientific justification:** None directly — this finding is about ethical-principle traceability, not evidence-tier integrity. Included for completeness since the review was asked to check constitutional conflicts broadly, not only Article IV/VIII matters.
- **Architectural impact:** One sentence added to the design's Constitutional basis or a new short subsection stating Article VII was considered and found non-applicable, with the specific reason (no individual-level clinical/genomic data, no dual-use design capability in this prototype's scope).
- **Risk:** Negligible either way.
- **Dependency:** None.
- **Blocks implementation:** No — this is a documentation completeness item with no bearing on what code does.
- **Recommended implementation phase:** Phase 002, added to the design before Approval, not gating the start of coding.
- **Traceability:** PHASE_002_REVIEW.md Section 1, CC1.

---

## 2. Scientific Integrity Risks

### SI1 — Allow-list presented as standing in for E1's rubric — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** Cheap to caveat now; expensive to leave unstated once a real `DATA/` connector cites this prototype as precedent for skipping a real per-source rubric.
- **Constitutional justification:** VISION.md Article VIII (tiers must not blur); GRAPH/SCHEMA.md's E1 rule (ingestion-time rubric requirement).
- **Scientific justification:** Directly protects the Evidence Model's `established_evidence` gate from being satisfied by a coarser instrument (source-level trust) than the constitution requires (source-*and-record* level rubric) — the exact kind of substitution VISION.md Article VIII treats as the platform's central risk if left unexamined.
- **Architectural impact:** One caveat sentence added to Section 5.2, stating the allow-list is a scope simplification valid only for this prototype's hand-authored seed data and sets no precedent for real ingestion connectors.
- **Risk:** Low to adopt; moderate to defer — the longer this goes unstated, the more likely a future connector's design silently inherits the simplification as if it were the actual standard.
- **Dependency:** None.
- **Blocks implementation:** No — the mechanism as designed is internally sound *for this prototype's own scope*; only the precedent-setting risk needs closing, and that's a documentation fix, not a gate-logic change.
- **Recommended implementation phase:** Phase 002, added to the design before Approval.
- **Traceability:** PHASE_002_REVIEW.md Section 2, SI1.

### SI2 — `source_asserts_causation` self-certifying — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** As designed, a boolean flag with no evidentiary backing is trivially satisfiable by anyone authoring a seed row — the entire point of E2 (never default to a causal predicate without source support) is defeated by a flag that requires no proof of that support. This is not a documentation gap; it is a gate-logic weakness that would ship a working-looking but non-enforcing implementation of one of the review's own most safety-critical rules.
- **Constitutional justification:** VISION.md Article VIII (Scientific Integrity as Supreme Constraint — "rejected, regardless of what phase XERDNA is in or what would be more convenient to ship"); GRAPH/SCHEMA.md E2.
- **Scientific justification:** E2 exists specifically to prevent a correlational finding from being silently strengthened into a causal claim — a self-certifying flag with no evidentiary trace reintroduces exactly that risk one layer down (the *predicate* is correctly gated, but the *gate's own input* isn't), which is a more subtle but equally real instance of the tier-blurring VISION.md Article VIII forbids.
- **Architectural impact:** `source_asserts_causation` is redefined to require an accompanying source-passage reference (mirroring Anti-Hallucination Rule 2's `source_span` field, once WVS1 is also applied), not just a boolean — the gate then checks for presence of that reference, not merely a flag's value.
- **Risk:** Low to adopt now; high to defer — once real predicate data exists, retrofitting an evidentiary requirement onto a boolean-only field means re-auditing every prior `causes` insertion to determine whether it was ever actually justified.
- **Dependency:** Benefits from WVS1 being applied first (so `source_span`-style fields already exist in the canonical schema to reuse the same pattern for).
- **Blocks implementation:** **Yes.** An implementer following Section 4.3/5.2 as currently written would build a gate that does not actually enforce E2 in substance, only in appearance.
- **Recommended implementation phase:** Phase 002, design correction applied before Implementation begins.
- **Traceability:** PHASE_002_REVIEW.md Section 2, SI2.

### SI3 — `infores:` CURIE convention unspecified — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** Cheap clarification of an already-existing field's expected value format; costs nothing to state and prevents inconsistent, ad hoc source-naming in seed data the moment more than one contributor writes rows.
- **Constitutional justification:** MASTER_CONTEXT.md Article V Rule 4 (prefer standards the field already converged on); GRAPH/SCHEMA.md's Provenance Model and the v1.2 `biolink:InformationResource` correction.
- **Scientific justification:** Directly carries forward the B2 finding's resolution — GRAPH/SCHEMA.md was specifically corrected to point provenance representation at `infores:` CURIEs rather than a (non-existent) `biolink:InformationResource` node category; a design that doesn't restate this convention risks quietly reintroducing the ambiguity B2 just closed.
- **Architectural impact:** Section 4.1/4.3's `primary_knowledge_source`/`aggregator_knowledge_source` field descriptions gain an explicit "follows the `infores:` CURIE convention" note.
- **Risk:** Low either way — but adopting now costs one sentence, while deferring risks divergent source-naming across whatever seed rows get authored first.
- **Dependency:** None.
- **Blocks implementation:** No — the field already exists and is required; only its value-format convention is being made explicit, which an implementer familiar with GRAPH/SCHEMA.md's own Provenance Model examples (`infores:uniprot`, `infores:alphafold`) would likely infer correctly regardless.
- **Recommended implementation phase:** Phase 002, added to the design before Approval.
- **Traceability:** PHASE_002_REVIEW.md Section 2, SI3.

---

## 3. Missing Enforcement Points

### MEP1 — Hypothesis Model's established-evidence mechanism unmodeled — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** This is the review's most structurally significant finding alongside WVS1. GRAPH/SCHEMA.md states plainly that a hypothesis `status` transition to `refuted`/`supported_by_experiment` is *itself* an `established_evidence` event — a second, distinct pathway to that tier, separate from the Prediction Model's promotion mechanism. The design as written has no representation of this second pathway at all, and `promoted_from`'s unrestricted typing means the two mechanisms could be silently conflated by an implementer who didn't independently know they were meant to be distinct.
- **Constitutional justification:** VISION.md Article VIII (tier separation is load-bearing at every surface); GRAPH/SCHEMA.md's Hypothesis Model rule (status transitions are themselves established_evidence events) and Prediction Model rule (promotion is linked to, not substituted for, the original).
- **Scientific justification:** This is squarely about evidence-tier integrity — a hypothesis "resolving" into established fact and a prediction being independently confirmed are different scientific events with different provenance chains (an experiment's finding, versus an independent citation of a confirming study). Conflating their storage representation risks losing the distinction between "a researcher validated this hypothesis" and "an unrelated data point happened to confirm a model's guess" — exactly the kind of collapsed nuance VISION.md Article IV's three-tier model exists to prevent.
- **Architectural impact:** A second, explicit resolution mechanism is added to Section 4.5/5 (a hypothesis `status` transition to `supported_by_experiment`/`refuted` triggers, or requires, insertion of its own linked `established_evidence` record), and `promoted_from` (Section 4.3) is constrained to only reference `computational_prediction`-tier records, closing off the ambiguous case.
- **Risk:** Low to adopt now, while no hypothesis-tier records exist yet in any real dataset; high to defer, since retrofitting a second resolution pathway after hypotheses have already been (incorrectly) resolved via the prediction pathway would require re-auditing every such record's provenance chain.
- **Dependency:** None.
- **Blocks implementation:** **Yes.** An implementer following the design as written has no correct way to represent a resolved hypothesis, and no protection against `promoted_from` being misused for that purpose.
- **Recommended implementation phase:** Phase 002, design correction applied before Implementation begins.
- **Traceability:** PHASE_002_REVIEW.md Section 3, MEP1.

### MEP2 — No test for allow-list rejection path — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** IMPLEMENTATION_POLICY.md Section 6 requires every enforced rule to have a corresponding test; the allow-list mechanism (Section 5.2) is correctly specified but currently unproven by anything in Section 7 or 8.
- **Constitutional justification:** MASTER_CONTEXT.md Article XII stage 9 (Validation); IMPLEMENTATION_POLICY.md Section 6.
- **Scientific justification:** An untested gate is a gate whose correctness is asserted, not demonstrated — for a rule this closely tied to E1's evidence-tiering discipline, "asserted but unproven" is a meaningfully weaker guarantee than every other tier-boundary rule in the design, which does have a corresponding test.
- **Architectural impact:** One seed/test case added: an `established_evidence` insert attempted against a source not on the allow-list, expected to be rejected.
- **Risk:** Low to adopt; the mechanism itself is not believed broken, only unproven — so the risk of deferring is a false sense of confidence, not a live defect.
- **Dependency:** None; can be added independently of any other finding.
- **Blocks implementation:** No — the underlying gate logic (Section 5.2) is already correctly specified; this closes a proof gap, not a design gap, and can be added during the Testing/Validation stage without delaying the start of coding.
- **Recommended implementation phase:** Phase 002, Testing/Validation stage.
- **Traceability:** PHASE_002_REVIEW.md Section 3, MEP2.

### MEP3 — `status` value set unvalidated — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** As designed, `status` is "required, defaults to active" with no stated constraint on what other values are acceptable — an implementer following the design literally would accept any string, defeating E3's entire purpose (a bounded, meaningful lifecycle: `active` / `retracted` / `superseded_by:<id>`).
- **Constitutional justification:** MASTER_CONTEXT.md Article IV (provenance and traceability prioritized over convenience); GRAPH/SCHEMA.md's E3 rule.
- **Scientific justification:** An unbounded `status` field can silently accumulate meaningless or contradictory values over the platform's lifetime — directly undermining the retraction/supersession tracking E3 was accepted specifically to enable (originally a `Critical`-severity finding in GRAPH/SCHEMA_REVIEW.md), and doing so in a way that would not surface as an error until a much later phase tries to consume the field and finds it unreliable.
- **Architectural impact:** Section 4.1/4.3 and Section 5.1 gain an explicit constraint: `status` must be one of the three valid forms, with `superseded_by:<id>` validated against an existing record ID at insert time.
- **Risk:** Low to adopt now, before any real status transitions occur; high to defer, since an unvalidated field that's already accumulated inconsistent values is far harder to clean up than to constrain from the start.
- **Dependency:** None.
- **Blocks implementation:** **Yes.** This is a genuine gate-logic gap, not merely a missing test — nothing in the current design prevents an invalid `status` value from being accepted.
- **Recommended implementation phase:** Phase 002, design correction applied before Implementation begins.
- **Traceability:** PHASE_002_REVIEW.md Section 3, MEP3.

### MEP4 — `schema_version` immutability unstated — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** `evidence_tier` and `xerdna_id` are explicitly called out as immutable post-insert (Section 4.1); `schema_version` is not, despite depending on exactly the same guarantee to do its job — R1's whole purpose is letting a future reader trust that a record's `schema_version` reflects what it was actually created under, which a mutable field cannot guarantee.
- **Constitutional justification:** VISION.md Article IX ("Build for 2,000 phases" — R1 is explicitly the concrete mechanism protecting this); GRAPH/SCHEMA_DECISIONS.md R1 (rated the clearest instance of the exact failure mode Article IX exists to prevent).
- **Scientific justification:** Indirect but real — `schema_version` is what lets future scientific reasoning over the graph correctly interpret a record's field set (e.g., knowing a pre-v1.2 record legitimately lacks the `resolution_status` field WVS1 would add, rather than treating its absence as a data-quality error). A mutable `schema_version` breaks that interpretive guarantee silently.
- **Architectural impact:** `schema_version` added to the immutability guarantee already specified for `evidence_tier`/`xerdna_id` in Section 4.1 and enforced via the same two-layer (application + storage trigger) mechanism in Section 5.3.
- **Risk:** Low to adopt; the omission is cheap to close because no `schema_version` mutation has occurred yet (nothing has been implemented) — this is exactly the "cheap now, expensive after data exists" pattern this project has named repeatedly.
- **Dependency:** None.
- **Blocks implementation:** **Yes.** Building the immutability trigger for only two of the three fields that need it, because the design only names two, would leave a real gap in an implementation that otherwise faithfully followed the design.
- **Recommended implementation phase:** Phase 002, design correction applied before Implementation begins.
- **Traceability:** PHASE_002_REVIEW.md Section 3, MEP4.

### MEP5 — T15 has no corresponding seed data — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** A listed test that has nothing in the seed data to actually exercise it is a test that will either fail to compile/run or trivially pass without meaning anything — cheap to fix by either connecting T15 to the existing split/merge seed row (which does use `xerdna:` predicates) or adding a dedicated case.
- **Constitutional justification:** IMPLEMENTATION_POLICY.md Section 6 (every enforced rule needs a real, working test, not a nominal one).
- **Scientific justification:** None directly — this is a testing-completeness issue for the Namespace Registry mechanism (B4's extended scope), not an evidence-tier matter.
- **Architectural impact:** Section 7 or Section 8 clarified to state explicitly that T15 is exercised via the `entity_lineage` seed row's use of `xerdna:split_into`/`xerdna:merged_from`, or a standalone case is added if that connection is judged too indirect.
- **Risk:** Low either way — the underlying registry-scope mechanism (Section 4.9) is not in question, only whether the test as listed can actually run against real seed data.
- **Dependency:** None.
- **Blocks implementation:** No — the registry gate logic itself (Section 4.9) is correctly specified; this is a test-authoring clarification.
- **Recommended implementation phase:** Phase 002, Testing/Validation stage.
- **Traceability:** PHASE_002_REVIEW.md Section 3, MEP5.

---

## 4. Weak Validation Strategy

### WVS1 — Section 6 fields missing from Sections 4–5's canonical structure — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** This is the review's other most structurally significant finding. `source_span`, `resolution_status`, and `basis` are described in Section 6 as real, required enforcement fields, but do not appear anywhere in Section 4's field tables or Section 5's gate-check lists — the two halves of the same design document disagree about what the schema actually contains. An implementer building strictly from the "storage structure" and "gate" sections (the sections that actually define what to build) would never discover these fields exist.
- **Constitutional justification:** MASTER_CONTEXT.md Article V Rule 1 (typed, never ad hoc — an internally inconsistent design risks producing exactly the kind of ad hoc, undocumented field the constitution warns against); VISION.md Article VI (AI Principles — the Anti-Hallucination Rules Section 6 claims to enforce must actually be enforced, not merely described).
- **Scientific justification:** Several of the affected fields (`resolution_status` for Anti-Hallucination Rule 4, `basis` for Rule 6) are direct mechanisms protecting against exactly the kind of unverified-but-plausible-looking claims VISION.md Article VIII treats as the platform's central risk. A design whose own sections disagree about whether these fields exist is a design that cannot be trusted to deliver the protection it claims.
- **Architectural impact:** `source_span`, `resolution_status`, and `basis` added to the appropriate Section 4 field tables (`associations`, `confidence`) and Section 5's gate-check descriptions, so all three sections are drawn from one consistent field inventory.
- **Risk:** Low to adopt now, before any code exists; high to defer, since an implementation built from the inconsistent version would need to be revised after the fact once the gap is discovered — likely during Validation, the most expensive point to discover a structural design gap.
- **Dependency:** None; this should be applied before SI2 and MEP1's fixes, since both benefit from `source_span`-style fields already being part of the canonical structure.
- **Blocks implementation:** **Yes.** This is the clearest blocking finding in the entire review — Sections 4–5 as currently written cannot deliver what Section 6 claims.
- **Recommended implementation phase:** Phase 002, design correction applied before Implementation begins, and applied first among the design corrections (Section 6 alignment should land before SI2/MEP1's more specific fixes, which build on the same fields).
- **Traceability:** PHASE_002_REVIEW.md Section 4, WVS1.

### WVS2 — Read-path enforcement weak — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** The finding is real but scoped narrowly to *future* risk rather than a defect in what this prototype itself needs to do — a single, correctly-written read function can satisfy the rule today. The value of accepting this now is architectural: naming the risk explicitly means Phase 2/3 (Roadmap numbering), which will build the first additional read paths on top of this storage layer, inherits the requirement as a known constraint rather than discovering it the hard way.
- **Constitutional justification:** GRAPH/SCHEMA.md's Scientific Integrity Constraint 2 ("any future API, UI, or export path that can return graph data without also surfacing its evidence_tier and primary_knowledge_source is a constitutional violation... not a missing feature to add later").
- **Scientific justification:** Directly protects the visibility of evidence tiers at every future query surface — VISION.md Article VII Rule 5 ("honesty about what the system is") depends on this holding at every future read path, not just this prototype's first one.
- **Architectural impact:** A design note added describing a single canonical query layer that always joins tier and source, with no lower-level accessor exposed that could bypass it — a structural pattern for this prototype to establish now, so later phases extend it rather than inventing their own read path from scratch.
- **Risk:** Low to adopt (a note costs nothing); the residual risk this doesn't fully close is that a *future* phase's read path might still bypass the pattern despite the note — mitigated only by the note existing at all, not eliminated by it.
- **Dependency:** None for this prototype; genuinely closing the risk depends on Phase 2/3 (Roadmap numbering) actually following the pattern when it's built.
- **Blocks implementation:** No, for this prototype's own scope — its single read function can be built correctly without further design work. The finding is accepted for its forward-looking value, not because Phase 002 itself cannot proceed without it.
- **Recommended implementation phase:** Phase 002 (a design note now); the structural guarantee itself matures when Phase 2/3 (Roadmap Article III) builds its first additional read path.
- **Traceability:** PHASE_002_REVIEW.md Section 4, WVS2.

### WVS3 — SQLite pragma/trigger specifics unstated — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** This is a concrete, well-known implementation trap (SQLite's foreign keys are off by default per connection) that could produce an implementation that looks correct — passes a casual read-through — while silently not enforcing referential integrity at all. The `CHECK`-vs-trigger distinction for immutability is the same category of risk: building the wrong mechanism produces something that appears to satisfy Section 5.3 without actually doing so.
- **Constitutional justification:** MASTER_CONTEXT.md Article V Rule 2 (provenance is mandatory, not optional metadata — silently-unenforced foreign keys would let orphaned or malformed provenance links into the graph); IMPLEMENTATION_POLICY.md Section 5 (validation must confirm constraints are actually enforced at runtime, not merely intended).
- **Scientific justification:** Referential integrity underlies nearly every scientific guarantee this design makes — xrefs resolving to real nodes, associations pointing at real subjects/objects, split/merge lineage pointing at real prior IDs. If foreign keys are silently unenforced, none of these guarantees actually hold, even though the design document elsewhere describes them as enforced.
- **Architectural impact:** Section 3 or Section 5 gains an explicit statement that `PRAGMA foreign_keys = ON` is set on every connection, and that immutability (Section 5.3) is implemented via `BEFORE UPDATE` triggers specifically, not `CHECK` constraints.
- **Risk:** Low to adopt; high to defer, since this is exactly the kind of implementation detail that, if gotten wrong, would not be caught by casual testing (the schema would look right, and only a deliberate test of "can I actually insert an orphaned reference" would catch it — which is why MEP2/MEP5's testing discipline matters alongside this).
- **Dependency:** None.
- **Blocks implementation:** **Yes.** An implementer could very plausibly build this prototype without setting the foreign-key pragma or without realizing a trigger (not a `CHECK` constraint) is required for immutability, producing something that silently fails to enforce what the design claims.
- **Recommended implementation phase:** Phase 002, design correction applied before Implementation begins.
- **Traceability:** PHASE_002_REVIEW.md Section 4, WVS3.

### WVS4 — Python version unpinned — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** Trivial to fix, and consistent with this project's own established discipline (O1) of pinning versions explicitly wherever reproducibility depends on it.
- **Constitutional justification:** VISION.md Article V Rule 4 (reproducibility over cleverness).
- **Scientific justification:** None directly — this is a build-reproducibility concern, not an evidence-tier matter.
- **Architectural impact:** Section 3 states a minimum Python version explicitly (e.g. "Python ≥ 3.10").
- **Risk:** Negligible either way.
- **Dependency:** None.
- **Blocks implementation:** No.
- **Recommended implementation phase:** Phase 002, added to the design before Approval.
- **Traceability:** PHASE_002_REVIEW.md Section 4, WVS4.

---

## 5. Traceability Gaps

### TG1 — No target code directory specified — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** This is, in the most literal sense, a prerequisite to writing any code at all — someone has to decide where the files go, and per MASTER_CONTEXT.md Article VI/IX, that decision is a naming-convention matter the design document should settle explicitly, not leave to whoever happens to write the first file.
- **Constitutional justification:** MASTER_CONTEXT.md Article VI Rule 3 (design documents "must open with a pointer back to the constitutional article that authorizes them" — the same explicitness this project extends to *where implementation lives*, not only what authorizes it); Article IX (Repository Structure).
- **Scientific justification:** None directly — a structural/organizational matter, not a tier-integrity one.
- **Architectural impact:** The design states explicitly where implementation code will live — recommended: `GRAPH/engine/`, extending the folder MASTER_CONTEXT.md Article IX already assigns to "the biological knowledge graph itself," consistent with Article V Rule 3's extend-over-invent preference, rather than introducing a new top-level folder for a single prototype.
- **Risk:** Low to adopt; without it, whoever writes the first file makes this decision ad hoc and unrecorded, which is a minor but real violation of this project's own documentation discipline.
- **Dependency:** None.
- **Blocks implementation:** **Yes**, trivially — code cannot be written without a location to write it in, and that location should be a recorded design decision, not an implementer's unrecorded choice.
- **Recommended implementation phase:** Phase 002, design correction applied before Implementation begins.
- **Traceability:** PHASE_002_REVIEW.md Section 5, TG1.

### TG2 — Traceability manifest incomplete — **ACCEPT NOW**

- **Decision:** ACCEPT NOW.
- **Reason:** Cheap to extend; the existing 6-row manifest is correct as far as it goes, just not comprehensive relative to the ~16 rules and 9 tables the design actually specifies.
- **Constitutional justification:** IMPLEMENTATION_POLICY.md Section 3 (Architectural Traceability).
- **Scientific justification:** None directly.
- **Architectural impact:** Section 10 extended to cover the Hypothesis Model, Confidence Model, and Anti-Hallucination Rule enforcement points currently missing from the manifest.
- **Risk:** Negligible either way.
- **Dependency:** Best done after WVS1, MEP1, and SI2 are applied, so the manifest reflects the corrected field set rather than needing a second pass.
- **Blocks implementation:** No — a documentation-completeness matter, useful for future auditors but not required for an implementer to build correctly from Sections 4–8.
- **Recommended implementation phase:** Phase 002, Validation-stage documentation, after the blocking corrections above are applied.
- **Traceability:** PHASE_002_REVIEW.md Section 5, TG2.

### TG3 — Review independence limited — **DEFER**

- **Decision:** DEFER.
- **Reason:** This is a valid, honestly-recorded observation about how this specific review was conducted, not a defect in PHASE_002_DESIGN.md itself — there is nothing to edit in the design document to "fix" it, and no substitute independent reviewer is available to assign this to right now. Designing a formal second-reviewer requirement today, for a review process that has so far always been conducted by the same single actor across every stage, would be process-building ahead of any concrete evidence that self-review has actually produced a missed error — the same reasoning GRAPH/SCHEMA_DECISIONS.md applied to R3 (new namespace-registry governance for multi-contributor scale), which was REJECTed on comparable grounds. This finding is DEFERRED rather than REJECTED because, unlike R3, the underlying concern here is not speculative — it is a demonstrated, present-tense limitation of this exact review — it is simply not actionable as a design edit today.
- **Constitutional justification:** MASTER_CONTEXT.md Article IV (not a license to over-build speculative process; a lightweight acknowledgment now, revisited with evidence later, is preferred over inventing a heavier review process with no track record to design against).
- **Scientific justification:** None directly.
- **Architectural impact:** None to PHASE_002_DESIGN.md. This finding's resolution is procedural, not architectural.
- **Risk:** Moderate and ongoing — every stage of this pipeline, across both Phase 001 and Phase 002, has so far been conducted by the same underlying actor across Architecture, Review, Decision, Audit, and Approval roles, even when explicitly reframed as an "independent Board." This is a standing characteristic of the current process, not unique to this one finding.
- **Dependency:** Availability of a genuinely independent reviewer (a different agent configuration, or human review) for a future high-stakes stage — most importantly, before Phase 002's own eventual Approval, and certainly before any phase whose implementation would be difficult to reverse.
- **Blocks implementation:** No.
- **Recommended implementation phase:** Not phase-specific — an ongoing practice recommendation. Revisit explicitly at Phase 002's Approval stage, and flag again if it recurs at Phase 003 and beyond, so it accumulates as tracked evidence rather than being re-discovered from scratch each time.
- **Traceability:** PHASE_002_REVIEW.md Section 5, TG3; PHASE_002_REVIEW.md's own opening "limitation of this review" note.

---

## What Happens Next

This document authorizes nothing by itself. Per Scientific Constitution Before Code (VISION.md Article IX), the 15 ACCEPT NOW items become real only when applied to PHASE_002_DESIGN.md as explicit, individually traceable edits — a separate, subsequent Remediation-stage step requiring its own go-ahead, mirroring exactly how GRAPH/SCHEMA_DECISIONS.md's ACCEPT NOW items were later applied to GRAPH/SCHEMA.md. Of those 15, **7 block Implementation outright** (SI2, MEP1, MEP3, MEP4, WVS1, WVS3, TG1) and must be resolved before any code is written; the other 8 are accepted but may be closed during design polish, the Testing/Validation stage, or — in WVS2's case — inherited as a constraint by a later Roadmap phase. The 1 DEFER item (TG3) remains visible here as a standing, ongoing practice note, revisited at Phase 002's own Approval stage rather than forgotten. No item was REJECTed.
