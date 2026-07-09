# PHASE 001 APPROVAL — V2 (Independent Review)

**Prepared by:** the independent XERDNA Scientific Architecture Review Board.
**Status:** Governance record, not implementation. This document does not reuse, defer to, or incorporate by reference any conclusion from `DOCS/PHASE_001_APPROVAL.md` (V1) — Phase 1 is evaluated here as if no prior approval determination had ever been made. This is the Approval stage (MASTER_CONTEXT.md Article XII, stage 7) following the independent, first-principles Audit in `DOCS/ARCHITECTURE_AUDIT_V2.md`. This review is understood to determine whether the first implementation in XERDNA's history is permitted to begin.

---

## Readiness Assessment

### Constitutional Readiness — Not Ready

VISION.md, ROADMAP.md, and MASTER_CONTEXT.md (now v1.1, including the ratified Article XII) were independently re-read in full. The governance pipeline is genuinely, not nominally, constitutional — verified directly, not assumed. However, this review's own Audit (Section 4) surfaced a defect inside the ratified constitutional text itself, not introduced by any of this session's edits: MASTER_CONTEXT.md Article X lists the four constitutional documents in an order that does not match Article I's Authority Hierarchy, with nothing in either article stating these describe different axes (orientation order vs. precedence order). This is a foundational-layer ambiguity, not a downstream one, and this Board declines to treat "probably harmless" as equivalent to "resolved," particularly given this project has already set the precedent — in ratifying Article XII — that this exact class of ambiguity warrants an explicit amendment, not an informal read-around.

### Architectural Readiness — Not Ready

GRAPH/SCHEMA.md v1.1 is well-constructed: all 15 ACCEPT NOW items from GRAPH/SCHEMA_DECISIONS.md are correctly incorporated, traceable, and non-contradictory with the constitution. Independently re-verified, not inherited. Two issues remain:

- The `xerdna:` Namespace Registry's governance scope is ambiguous between entity-type prefixes (its only stated examples) and relationship predicates (of which SCHEMA.md now mints five, including two — `xerdna:split_into`, `xerdna:merged_from` — added in this session's own Blocker 3 work). The registry's discipline is not demonstrably being applied to the fastest-growing category of new terms.
- Two smaller, longer-standing architectural items remain open from the prior audit round (GRAPH/SCHEMA_DECISIONS.md R2 partly self-citing SCHEMA.md as "constitutional justification"; SCHEMA.md's Disease/Phenotype/Anatomy addition extending ROADMAP's Phase 1 entity list via a general principle rather than a ROADMAP-side acknowledgment) — neither newly found this pass, both still unresolved.

### Scientific Readiness — Not Ready

This is the dimension this Board weighs most heavily, consistent with the standing instruction that scientific accuracy takes precedence over speed. Two gaps:

- The Biolink Model / OBO ontology *versions* used in SCHEMA.md are honestly pinned and were independently re-verified by this Board via live lookup — this part of the work is sound. What has not been done is a full, term-by-term verification that the ~19 Biolink entity categories and the predicates cited throughout SCHEMA.md (including the two newly added in this session's Blocker 3 work, `biolink:correlated_with` as a default and `biolink:causes` as the example to avoid) actually exist, unchanged in meaning, under the specific pinned Biolink v4.3.7 release — as opposed to some other, unspecified Biolink version. This Board's own spot-check of three core terms (`biolink:Genome`, `biolink:SequenceVariant`, `biolink:PopulationOfIndividualOrganisms`) found no errors, which is reassuring but is not the same as a complete verification.
- The newly-added Checked-Absent Records section (from P1) is not reconciled against MASTER_CONTEXT.md Article II Rule 1 — a Non-Negotiable Rule requiring every piece of data entering the graph to carry one of the three evidence tiers. The most likely correct resolution (that a checked-absent record is process metadata, not a biological claim, and is therefore exempt) is not stated in the document itself. An unstated exemption to a Non-Negotiable Rule, however probably benign, is not the same as a stated one.

### Governance Readiness — Ready, with one procedural note

The pipeline itself (Article XII) is soundly ratified and functioning as designed — this very document is evidence of that, since it exists specifically because DOCS/PHASE_001_APPROVAL.md (V1) went stale and the pipeline's own discipline calls for superseding it rather than silently editing it. That staleness is not treated as a Governance blocker here, because superseding it is exactly what this document does by existing. One minor, non-blocking item remains: DOCS/ARCHITECTURE_AUDIT.md (V1)'s self-description ("does not self-assign a level") is now outdated relative to the ratified Article I amendment — cosmetic, not a governance defect in substance.

---

## Blockers, Ordered by Category (Constitutional → Scientific → Architectural → Governance → Editorial)

### 1. Constitutional

**B1 — Article X's document ordering conflicts, in appearance, with Article I's Authority Hierarchy, with no clause distinguishing the two.** MASTER_CONTEXT.md Article X ("How the Constitutional Documents Fit Together") lists README → VISION → ROADMAP → MASTER_CONTEXT; Article I's actual precedence is VISION → MASTER_CONTEXT → ROADMAP → README. Closing this requires either a small Article III amendment (a clarifying sentence in Article X stating it describes expository, not precedence, order) or, at minimum, an explicit Board-level determination that no amendment is needed and why — neither has occurred. See DOCS/ARCHITECTURE_AUDIT_V2.md Section 4.

### 2. Scientific

**B2 — Biolink/OBO entity and predicate names have not been fully verified against the pinned Biolink Model v4.3.7 release.** Spot-checks passed; a complete term-by-term pass has not been performed. Required before any implementation that treats these names as load-bearing (most acutely, the first `DATA/` ingestion connector). See DOCS/ARCHITECTURE_AUDIT_V2.md Section 7.

**B3 — Checked-Absent Records are not reconciled against Article II Rule 1's blanket evidence-tiering requirement.** A one-paragraph clarification in GRAPH/SCHEMA.md stating whether and why `checked_absent` records are exempt from the tier requirement (and from the "every relationship is an association" rule) is needed before this section can be considered complete. See DOCS/ARCHITECTURE_AUDIT_V2.md Section 8.

### 3. Architectural

**B4 — The `xerdna:` Namespace Registry's governance scope does not clearly cover relationship predicates**, despite five already being minted (two added in this session alone). Before further predicates are added — and certainly before an ingestion connector relies on any of them being governed — the registry's scope needs to be stated explicitly one way or the other. See DOCS/ARCHITECTURE_AUDIT_V2.md Section 17.

### 4. Governance

*No blocking findings.* The pipeline itself is sound; the one governance-adjacent staleness issue (V1's approval document) is resolved by this document's existence, not left open.

### 5. Editorial

*No blocking findings.* The Low-severity wording items identified in DOCS/ARCHITECTURE_AUDIT_V2.md (the "ratified" terminology drift, the missing Article XII citation in SCHEMA.md's header, the Extensibility Rule's threefold restatement, the `possibly_same_as`/`possibly_duplicate_of` naming drift, and V1's now-outdated self-description) remain open as non-blocking backlog, tracked the same way GRAPH/SCHEMA_DECISIONS.md tracks its own DEFER items.

---

## Remaining Risks (independent of the blockers above)

- **SCHEMA.md remains untested against real ingestion data** — unchanged from every prior readiness assessment; this is a standing, self-acknowledged limitation of a conceptual-design-only phase, not new to this review.
- **8 DEFER and 2 REJECT items remain open by design** — re-confirmed intact this pass, not a defect.
- **Single point of failure in constitutional amendment authority** — long-horizon, non-urgent, unchanged.
- **This is the third Audit/Approval cycle for the same phase** — each cycle has surfaced genuinely new findings the previous cycle did not catch (V1 → prior V2 draft surfaced N1–N4; this independent pass surfaced C1, S1, S2, A1, none of which overlap with N1–N4). This pattern itself is worth naming: it suggests the audit discipline is functioning as intended (each pass digs deeper), but also that confidence any single pass has found *everything* should remain calibrated, not absolute.

---

## Final Decision

# NOT APPROVED

Four blockers — one Constitutional (B1), two Scientific (B2, B3), one Architectural (B4) — must be resolved before Phase 1 may proceed to Implementation. None require new science or a change of architectural direction; each is a clarification, a verification pass, or a scope statement that this Board has fully specified above. No Governance or Editorial finding rises to blocking severity in this independent review. Once B1–B4 are resolved, a subsequent Approval-stage document should supersede this one, following the same discipline that produced it.
