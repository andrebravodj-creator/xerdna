# MILESTONE 002 REVIEW

**Status:** Advisory. This document reviews `GRAPH/engine/gate.py`, the extensions to `GRAPH/engine/schema.sql`, `GRAPH/engine/config.py`, and `GRAPH/engine/tests/test_milestone_002.py` against DOCS/PHASE_002_DESIGN.md, DOCS/IMPLEMENTATION_POLICY.md, GRAPH/SCHEMA.md, and DOCS/MILESTONE_001_POSTMORTEM.md. It modifies no code and no other document. Per MASTER_CONTEXT.md Article XII, this is a Review-stage artifact examining completed Implementation (stage 8), preceding whatever Validation-stage record follows it.

**A limitation of this review, restated because it remains unresolved:** this review is conducted by the same actor who designed and implemented Milestone 002. DOCS/PHASE_002_REVIEW.md and DOCS/MILESTONE_001_POSTMORTEM.md both already named this gap; neither produced a resolution. It is named again here (Finding G10) rather than silently repeated a fourth time without comment.

**Method:** every function in `gate.py` was read against the specific PHASE_002_DESIGN.md subsection it claims to implement, checking not only "does this function exist" but "does it fail exactly the way the design says, and succeed only when the design says it should." Severity follows the Review-stage convention already established in this project (`Critical` / `Moderate` / `Minor`).

---

## 1. Constitutional Compliance

*Checked against: VISION.md Article II Rule 5 / Article VIII (evidence-tier integrity); MASTER_CONTEXT.md Article V Rule 2 (provenance mandatory).*

No outright violation of a Non-Negotiable Rule was found in what the gate actually enforces when used as intended. One finding concerns what happens when it is *not* used as intended:

| # | Finding | Severity |
|---|---|---|
| G3 | **The gate never verifies the connection it is given has `PRAGMA foreign_keys = ON`.** Every referential-integrity guarantee this milestone relies on — `subject_id`/`object_id` pointing at real nodes, `promoted_from`/`resolved_by` pointing at real associations, `node_xrefs`/`entity_lineage` pointing at real nodes — depends entirely on that pragma being set. `db.connect()` sets it correctly, and `db.py` even exposes `foreign_keys_enabled(conn)` as a ready-made check — but `gate.py` never calls it. `gate.py`'s own module docstring claims to be "the ONLY legal way to insert records into XERDNA," yet it accepts any `sqlite3.Connection` object as a parameter and silently trusts that the caller opened it correctly. A connection opened via a bare `sqlite3.connect()` anywhere else in a future module — a script, a `DATA/` connector, a test that forgets to use `db.connect()` — would pass every gate check and still silently accept a `subject_id` that points at nothing. | **Critical** |

## 2. Implementation Correctness

*Checked against: DOCS/PHASE_002_DESIGN.md Section 4.5 (Hypothesis Model field semantics).*

| # | Finding | Severity |
|---|---|---|
| G5 | **`insert_hypothesis()`'s `supporting_evidence` check doesn't accommodate the design's own stated allowance.** Section 4.5 says `supporting_evidence` is "Required (may be an empty, explicit list)" — the same shape of allowance `contradicting_evidence` gets, which is properly implemented via the `none_found_as_of` companion field. `supporting_evidence` has no equivalent companion or defined sentinel; the gate's check (`if not supporting_evidence: raise`) rejects any falsy value, meaning there is currently no way for a caller to represent "explicitly checked, genuinely no supporting evidence" without inventing an ad hoc non-empty string (e.g. typing the literal text `"none"`) — which the gate cannot distinguish from a real citation. | Moderate |
| G6 | **The `established_evidence`-forbids-confidence check has a silent gap.** It inspects only `confidence_type` and `confidence_value`; a caller who passes `confidence_basis` alone, with both of those left `None`, is neither rejected nor recorded — the value is silently dropped, since the confidence-row insert further down is gated on `confidence_type is not None`. The design says "no confidence row may be attached (**rejected** if attempted)" — a silent drop is a different, weaker behavior than a rejection. | Minor |

## 3. Scientific Integrity

*Checked against: the project's standing rule — never invent scientific metadata, always verify from authoritative sources — and GRAPH/SCHEMA.md's Anti-Hallucination Rule 4.*

| # | Finding | Severity |
|---|---|---|
| G4 | **The two values in `ESTABLISHED_EVIDENCE_SOURCE_ALLOWLIST` (`infores:hgnc`, `infores:uniprot`) were never verified against the InfoRes Registry before being committed.** PHASE_002_DESIGN.md correctly leaves the allow-list's *contents* to implementation ("hand-authored and tiny"), so choosing values is within delegated scope — but this project applied real, live verification to every Biolink/OBO term it committed during the B2 remediation (Phase 002 Design v1.2), specifically because "very likely correct" was judged an insufficient standard for a scientific identifier. These two values were written from general knowledge, not checked. Both are near-certainly correct — that is exactly the condition under which this project has previously insisted on verifying anyway, not treated confidence as a substitute for it. | Moderate |
| G9 | **Non-`xerdna:`-namespaced categories and predicates receive no validation against any real vocabulary.** `_check_namespace_registered()` only inspects `xerdna:`-prefixed terms; a bare string like `category="banana"` or `predicate="not_a_real_predicate"` passes through unchecked as long as it isn't `xerdna:`-prefixed. This is consistent with what PHASE_002_DESIGN.md actually specifies (only B4/the Namespace Registry was named as an enforcement point) — not an implementation departure — but it is worth naming as a real, structural gap the design itself leaves open, especially given how much verification effort this project has invested in the Biolink vocabulary elsewhere. | Minor |
| G7 | **E2's causal-predicate check is a single hardcoded literal (`biolink:causes`).** GRAPH/SCHEMA.md's E2 principle is framed generally ("a causal predicate (e.g. `biolink:causes`)"); PHASE_002_DESIGN.md's own restatement already narrows this to the literal predicate `causes` specifically. The implementation is faithful to the design as approved — this finding documents an inherited scope limitation, not a new one introduced by Milestone 002. | Minor |
| G8 | **E2's check inspects only `predicate`, never `qualifier`.** A qualifier-based causal assertion (O4's predicate-plus-qualifier pattern, e.g. a `regulates` predicate qualified as directionally causal) could in principle carry a causal claim without tripping the `source_span` requirement. PHASE_002_DESIGN.md doesn't address this interaction between O4 and E2 either — inherited, not introduced. | Minor |

## 4. Enforcement Completeness

*Checked against: DOCS/PHASE_002_DESIGN.md Section 5, Section 8 (Test Matrix).*

Every enforcement point named in the design's Test Matrix (T1–T18) has a corresponding, working implementation — re-verified directly against the current code during this review, not assumed from the closing summary. The gaps found are in defense-in-depth around that core, not in the core itself:

- G3 (above) is the primary finding in this category — restated here because it is specifically an *enforcement* gap, not just a constitutional-framing one.
- G1 (below, under Rollback Safety) is also an enforcement-completeness matter in practice: a function with no rollback path is a function whose failure mode is unenforced, not just untidy.

## 5. Missing Validation

*Checked against: DOCS/IMPLEMENTATION_POLICY.md Section 6 (Testing Requirements).*

| # | Finding | Severity |
|---|---|---|
| G13 | **No test exercises `insert_entity_lineage()`'s foreign-key-violation path** (an `old_xerdna_id` or `new_xerdna_id` that doesn't reference a real node). This is precisely the path that would have surfaced G1 (below) during development — the test suite's own gap and the implementation's own gap are the same gap, viewed from two sides. | Moderate |
| G12 | **`test_T14_read_path_not_implemented_this_milestone` is structurally weak.** It asserts a `query` attribute doesn't exist on the gate module — an attribute that was never going to exist regardless of whether the read-path exclusion was honored or not. It documents the scope boundary in the test suite (useful) but doesn't meaningfully test anything (the assertion cannot fail in any scenario this milestone could plausibly produce). | Minor |

## 6. Rollback Safety

*Checked against: DOCS/PHASE_002_DESIGN.md Section 5.3; DOCS/IMPLEMENTATION_POLICY.md Section 8 (Rollback Policy, applied here to within-transaction failure, not deployment rollback).*

| # | Finding | Severity |
|---|---|---|
| G1 | **`insert_entity_lineage()` has no `try`/`except`/`rollback` wrapping, unlike every other insert function in this module.** It performs zero pre-validation that `old_xerdna_id`/`new_xerdna_id` reference real nodes (no Python-level check; relies entirely on the FK constraint, which itself depends on G3 being resolved to even fire). If the `INSERT` raises `sqlite3.IntegrityError`, the exception propagates with no explicit rollback call, unlike `insert_node()`, `insert_association()`, `insert_hypothesis()`, and `resolve_hypothesis()`, which all follow the same defensive pattern. | Moderate |
| G2 | **`insert_checked_absent()` has the same structural gap** (no `try`/`except`/`rollback`), though its actual risk surface is much smaller — `checked_absent` has no foreign keys and every one of its fields is pre-validated in Python before the `INSERT` runs, so there is currently no realistic path to a mid-transaction failure. Flagged for consistency with the module's own established pattern, not because a live risk was found. | Minor |

Every other insert path in this milestone — `insert_node()`, `insert_association()` (and everything composed on top of it via `_commit=False`: `insert_hypothesis()`, `resolve_hypothesis()`) — was independently re-traced this review and confirmed to roll back correctly and completely on any failure, including the specific atomicity fix made mid-build (the `_commit` composition pattern), which holds up under this second look.

## 7. Traceability

*Checked against: DOCS/IMPLEMENTATION_POLICY.md Section 3 (Architectural Traceability).*

Traceability is strong throughout — every check in `gate.py` cites the specific design section, finding ID, or constitutional rule it implements, and `schema.sql`'s new trigger block cites Section 5.3 point 2 directly. One gap:

| # | Finding | Severity |
|---|---|---|
| G14 | **The allow-list's specific values (G4) are traceable to *why the mechanism exists* (SI1) but not to *why these two values specifically*.** There is no comment or record explaining the choice of HGNC and UniProt over any other source, or documenting that they were (or weren't) checked against anything. This is the traceability-side expression of G4 — even if G4 is closed by verifying the values, this finding would remain unless the verification itself is recorded somewhere a future reader can find it. | Minor |

## 8. Consistency With the Approved Design

*Checked against: DOCS/PHASE_002_DESIGN.md v1.2 in full; DOCS/MILESTONE_001_POSTMORTEM.md's recommendations.*

The implementation matches the design closely — every table, every field, every stated rule in Sections 4 and 5 has a corresponding, correctly-behaving implementation, independently re-verified this review rather than assumed from the build's own closing summary. Two consistency gaps, both procedural rather than code-level:

| # | Finding | Severity |
|---|---|---|
| G10 | **None of DOCS/MILESTONE_001_POSTMORTEM.md's seven recommendations were formally closed.** Recommendation #1 (close or formally re-DEFER the `aggregator_knowledge_source` gap) and #4 (make a non-deferred decision on review independence) were restated conversationally at Milestone 002's kickoff but never recorded in any document — no re-DEFER entry, no decision record. Recommendation #2 (pin the verified Python environment) was named in a closing summary but not persisted anywhere in the repository. Recommendation #6 (insert Section 7's seed data early) was not acted on — no seed data was inserted this milestone. A recommendation that is re-acknowledged verbally at the start of the next milestone, without a durable record, is functionally indistinguishable from a recommendation that was never made — this is the same failure mode MILESTONE_001_POSTMORTEM.md itself warned about regarding the review-independence DEFER cycle, now recurring one level up. | Moderate |
| G11 | **`ENGINE_VERSION` was not incremented.** It remains `"0.1.0"` after Milestone 002 added the entire Insertion Gate — a substantial capability change by any reasonable reading. IMPLEMENTATION_POLICY.md Section 9 requires version increments to be "recorded with what changed and why," the same discipline already applied to `GRAPH/SCHEMA.md`'s Schema Changelog and `DOCS/PHASE_002_DESIGN.md`'s Design Changelog — no equivalent changelog exists for the engine's own version history at all. | Moderate |

---

## Summary

Of 14 findings: **1 Critical**, **6 Moderate**, **7 Minor**.

- **G3** — the gate does not verify its own foundational assumption (foreign keys enabled) before relying on it for referential integrity, despite the mechanism to check (`db.foreign_keys_enabled()`) already existing in the codebase.

The remaining 13 findings do not undermine the core result: every rule in the design's Test Matrix (T1–T18) is genuinely, correctly enforced when the gate is used through `db.init_db()`/`db.connect()` as intended, and the atomicity of every composed insert path holds under a second, independent trace. G3 is the one place where "the ONLY legal way to insert records" is a claim the code doesn't yet fully back up on its own — everything else is either a smaller consistency gap (G1, G2, G5, G6), an inherited and previously-acknowledged design limitation (G7, G8, G9), a testing gap (G12, G13), or unfinished governance follow-through from the prior milestone's own postmortem (G10, G11, G14).

**This review recommends; it does not fix anything.** Per Scientific Constitution Before Code and this project's own established discipline, each finding above should be triaged into a Decision-stage document (ACCEPT NOW / DEFER / REJECT) before any of them is applied to `GRAPH/engine/`, mirroring exactly how DOCS/PHASE_002_REVIEW.md's findings were triaged into DOCS/PHASE_002_DECISIONS.md before DOCS/PHASE_002_DESIGN.md was corrected.
