# GOVERNANCE PIPELINE — CONSTITUTIONAL AMENDMENT PROPOSAL

**Prepared by:** the Founding Scientific Architecture Board of XERDNA.
**Status:** Proposal only. Nothing in this document amends README.md, MASTER_CONTEXT.md, VISION.md, or ROADMAP.md. Per MASTER_CONTEXT.md Article III, this proposal becomes real only when the founding architect explicitly ratifies it, an Amendment Log entry is recorded, and a version bump is applied — none of which happens here. This is the analysis and exact proposed text an amendment would need; it is not the amendment.

---

## 1. The Question

Should the governance pipeline —

**Constitution → Architecture → Review → Decision → Audit → Remediation → Approval → Implementation → Validation → Release**

— become a permanent constitutional rule, and if so, where?

## 2. Determination: Yes

The pipeline should be ratified into MASTER_CONTEXT.md. Reasoning:

1. **It is not a new kind of authority — it is the operational form of an authority that already exists.** VISION.md Article IX establishes Scientific Constitution Before Code as a permanent rule; MASTER_CONTEXT.md Article IV already exists specifically to elaborate that article "for operational use." The pipeline is exactly that kind of elaboration — it belongs in the document whose stated job is to do this, not in a new kind of document.
2. **It closes gaps this Board already found.** Audit Finding 4.2 (High) — the consultation order has no ratified home; Finding 4.1 (Medium) — no hierarchy level for review/decision/audit artifacts; Finding 5.3 (Medium) — no enforcement artifact for the consultation requirement. Ratifying the pipeline closes all three in one amendment rather than three separate ones.
3. **It does not conflict with anything already ratified.** Section 4 below performs the explicit check.
4. **It is reversible and additive.** Per MASTER_CONTEXT.md Article V Rule 5 (reversibility as a design criterion) and Article IV (extension over replacement), the proposed amendment adds one new article and enriches one existing definition — it rewrites nothing, contradicts nothing, and removes no existing rule.

## 3. Exact Documents to Amend

| Document | Amend? | Why / why not |
|---|---|---|
| **MASTER_CONTEXT.md** | **Yes** | The operating-law document; already houses the Authority Hierarchy (Article I) and Governance & Amendment Process (Article III) the pipeline extends. |
| VISION.md | No | Article IX already states the principle the pipeline operationalizes ("Scientific Constitution Before Code," "Build for 2,000 phases"). Both remain word-for-word unchanged — see Section 6. Touching VISION.md here would be redundant with what MASTER_CONTEXT.md Article IV already does. |
| ROADMAP.md | No | ROADMAP Article I already states "Phase advancement is a governed act... only once its technical designs trace back to ratified constitutional articles." That sentence is compatible with, and now given concrete mechanics by, the new MASTER_CONTEXT article — adding the same mechanics into ROADMAP.md as well would duplicate them. ROADMAP governs *which phase comes next*; the pipeline governs *what gates a phase's own work must pass*. These are different axes and each stays in its existing home. |
| README.md | No (optional) | README is explicitly non-authoritative (Article I) and exists only to orient a reader toward the other three documents. It already directs readers to MASTER_CONTEXT.md for governance. No change is required; a one-line pointer to the new article would be a harmless but non-mandatory addition, at the architect's discretion. |

**Minimum footprint: MASTER_CONTEXT.md only, two edits.**

## 4. Proposed Amendment Text

### 4a. New Article — Phase Governance Pipeline

Proposed as **Article XII**, appended after the existing Article XI (Amendment Log). This placement requires no renumbering of any existing article and no change to any existing cross-reference in this or any other document (verified — see Section 5). An alternative placement, inserting it before Article VIII and renumbering Articles VIII–XI to IX–XII, would read more thematically but touches four article numbers and one internal cross-reference (Article III Rule 3's "Amendment Log (Article XI)") for no substantive gain; the Board recommends the append-only form as the smaller amendment, per MASTER_CONTEXT.md Article V Rule 5, but leaves the final choice to the founding architect at ratification.

> ## Article XII — Phase Governance Pipeline
>
> Elaborating VISION.md Article IX for operational use, in the same manner as Article IV: every phase's work moves through the following gates, in order, before any stage of it is authoritative:
>
> 1. **Constitution** — the ratified constitutional documents (VISION.md, this document, ROADMAP.md) that all subsequent work must trace back to (Article I, Article II Rule 5).
> 2. **Architecture** — a phase-specific design document (Level 5, Article I) proposing a technical model for a ratified constitutional objective.
> 3. **Review** — a critique of that design document against the constitution, recording findings and severities without modifying the design document itself.
> 4. **Decision** — a classification of every review finding as ACCEPT NOW, DEFER, or REJECT, each with a stated rationale, impact, risk, dependency, constitutional justification, and owning phase.
> 5. **Audit** — a cross-document consistency check across the constitution and the phase's architecture, review, and decision documents, surfacing contradictions, circular dependencies, duplicated concepts, missing constitutional references, and architectural weaknesses.
> 6. **Remediation** — a plan addressing every finding the Audit rates at the severity this document or a future amendment designates as blocking, without yet modifying any document.
> 7. **Approval** — an explicit, single-valued decision — APPROVED or NOT APPROVED — on whether the phase may proceed to Implementation, stating constitutional, architectural, scientific, and governance readiness, and every unresolved blocker.
> 8. **Implementation** — code, schemas, infrastructure (Level 6, Article I), built only after Approval, and only to the extent of what was approved.
> 9. **Validation** — verifying the implementation matches the approved design and every constraint in the constitutional documents it traces to.
> 10. **Release** — the validated implementation is made available for use.
>
> No stage may be skipped. No phase may enter Implementation while any blocking finding from its own Audit stage remains unresolved (Article II Rule 5).
>
> This article governs *when* a document's contents may be acted on. It does not alter the Authority Hierarchy (Article I) — precedence between documents in a conflict is, and remains, decided by Article I alone, never by a document's position in this pipeline. It does not alter ROADMAP.md's phase sequencing (ROADMAP Article I) — this pipeline governs the gates within a single phase's own work; ROADMAP governs the order phases are taken up across the platform's lifetime. The two are independent axes and neither substitutes for the other.

### 4b. Amendment to Article I, Level 5

Current text:

> 5. **Phase-specific design documents** (e.g. `GRAPH/SCHEMA.md`) — technical designs for a specific phase. Must be traceable to an article in documents 1–3. If a design document conflicts with the constitution, the design document is wrong and is revised.

Proposed replacement:

> 5. **Phase-specific design documents, and the governance artifacts that examine them** (e.g. `GRAPH/SCHEMA.md`, and its Review, Decision, Audit, Remediation, and Approval documents per Article XII) — technical designs for a specific phase, and the process artifacts that critique, triage, audit, and gate them. All are peers at this level. Must be traceable to an article in documents 1–3. If any of them conflicts with the constitution, it is wrong and is revised.

This closes Audit Finding 4.1 (no hierarchy level for review/decision/audit documents) by making explicit what GRAPH/SCHEMA_REVIEW.md already informally claimed for itself ("Level-5... same as SCHEMA.md itself") — the amendment ratifies that claim rather than contradicting it, and now extends the same classification to GRAPH/SCHEMA_DECISIONS.md, DOCS/ARCHITECTURE_AUDIT.md, DOCS/ARCHITECTURE_REMEDIATION_PLAN.md, this document, and DOCS/PHASE_001_APPROVAL.md.

### 4c. Proposed Amendment Log Entry

For Article XI, to be added only at ratification (not applied here):

| Version | Date | Change | Rationale |
|---|---|---|---|
| 1.1 | *(date of ratification)* | Added Article XII (Phase Governance Pipeline); amended Article I Level 5 to include review/decision/audit/remediation/approval artifacts as peers of phase design documents | Formalize the ten-stage gate sequence (Constitution → Architecture → Review → Decision → Audit → Remediation → Approval → Implementation → Validation → Release) already applied in practice to Phase 1's GRAPH/ work, so it binds every future phase and every future reader — including one with no memory of the session in which this practice was first established — per Article III Rule 3. |

## 5. Circularity and Duplication Check

Performed explicitly, per this Board's instructions:

- **Article XII → Article I:** Article XII references Article I's Level 5/6 distinction. Article I does not need to reference Article XII for its own definitions to hold — Levels 1–6 are fully meaningful without the pipeline existing. One-directional. No cycle.
- **Article XII → VISION.md Article IX / MASTER_CONTEXT.md Article IV:** both already-ratified, both one-directional inputs to Article XII. Neither needs to change or reference Article XII back. No cycle.
- **Article XII → ROADMAP.md Article I:** Article XII explicitly disclaims overlap ("does not alter ROADMAP.md's phase sequencing"); ROADMAP.md needs no edit and gains no new dependency on Article XII — its existing "governed act" sentence remains true on its own terms, now with more concrete mechanics available elsewhere. No duplication: ROADMAP states the principle that phase advancement is governed; Article XII supplies the mechanics, in the document already responsible for mechanics (Article X, "How the Constitutional Documents Fit Together": MASTER_CONTEXT is "the operating law").
- **Article I Level 5 amendment → Article XII:** the amended Level 5 clause names document *types* (review, decision, audit, remediation, approval); Article XII names pipeline *stages*. They describe the same artifacts from two different, non-overlapping angles (classification vs. sequence) — this is cross-reference, not duplication, in the same way Article I and Article IX already cross-reference the Level 5/6 boundary without restating each other's content.
- **No existing cross-reference breaks:** confirmed by search — no document outside MASTER_CONTEXT.md cites "Article VIII," "Article IX," "Article X," or "Article XI" of MASTER_CONTEXT.md specifically (all such citations found in other documents are to VISION.md's or ROADMAP.md's own articles of the same number, which are unaffected). The append-only placement (Section 4a) touches zero existing citations.

## 6. Preservation of the Two Named Principles

- **"Scientific Constitution Before Code"** remains defined, word-for-word, only in VISION.md Article IX and restated (not redefined) in MASTER_CONTEXT.md Article II Rule 5 and README.md, exactly as today. Article XII does not restate it a fourth time — it cites it and operationalizes it, consistent with Article IV's existing pattern.
- **"Build for 2,000 phases, not the next 20"** remains defined, word-for-word, only in VISION.md Article IX and restated in MASTER_CONTEXT.md Article II Rule 4 and README.md, exactly as today. Article XII's rationale for existing (Amendment Log entry, Section 4c) cites this principle rather than redefining it.
- Neither principle's text changes. Article XII is subordinate to both, not a replacement for either — this is the same relationship Article IV already has to Article IX, extended by one article rather than altered.

## 7. What Happens Next

This proposal requires the founding architect's explicit ratification through the Article III process before MASTER_CONTEXT.md is edited. Until then, the pipeline is Board practice by instruction, not yet binding text — this gap is itself the exact condition Audit Finding 4.2 identified, and it remains open until this proposal (or an amended version of it) is ratified. See DOCS/PHASE_001_APPROVAL.md for how this open gap bears on Phase 1's readiness to proceed.
