# ARCHITECTURE REMEDIATION PLAN

**Prepared by:** the Founding Scientific Architecture Board of XERDNA.
**Status:** Governance record, not implementation. This document does not modify README.md, MASTER_CONTEXT.md, VISION.md, ROADMAP.md, GRAPH/SCHEMA.md, GRAPH/SCHEMA_REVIEW.md, or GRAPH/SCHEMA_DECISIONS.md. It plans corrections; it does not apply them. Per the governance pipeline now in effect (Constitution → Architecture → Review → Decision → Audit → **Remediation** → Approval → Implementation → Validation → Release), this document is the Remediation stage output for the three `High`-severity findings raised in [DOCS/ARCHITECTURE_AUDIT.md](ARCHITECTURE_AUDIT.md). No implementation may begin until each finding below is resolved, per this session's standing rule.

**Scope:** this plan covers only the three `High` findings (1.1, 1.2, 4.2). The `Medium` and `Low` findings remain a tracked backlog in ARCHITECTURE_AUDIT.md and are not blocking under the rule as stated.

---

## R1 — Stale "Current State" claims and ambiguous use of "schema" (Audit Finding 1.1)

- **Problem:** README.md's "Status" section and MASTER_CONTEXT.md Article VIII both assert "No application code, schema, or implementation has been authorized yet." GRAPH/SCHEMA.md — a substantive, constitutionally-grounded conceptual design — already exists, as does its review and its ratified decisions log. Taken literally, the claim is now false. The underlying cause is that Article I uses the word "schema" for two different things: a Level-5 conceptual design document (`GRAPH/SCHEMA.md` is Article I's own example) and a Level-6 implemented database schema, without ever saying so.
- **Affected constitutional articles:** MASTER_CONTEXT.md Article I (Levels 5 and 6 — the terminology ambiguity), Article VIII (Current State — the stale claim itself), Article III Rule 2 (governs whether this fix is an amendment).
- **Affected documents:** README.md ("Status" section); MASTER_CONTEXT.md (Article VIII primarily; Article I optionally, for the terminology fix).
- **Smallest possible correction:**
  1. Reword README.md's Status section to distinguish ratified conceptual design from unauthorized implementation, e.g.: *"This repository contains ratified constitutional documentation and Phase 1 conceptual architecture (GRAPH/SCHEMA.md and its governance artifacts). No implementation — database, ingestion pipeline, API, backend, or frontend code — has been authorized yet."*
  2. Apply the same distinction to MASTER_CONTEXT.md Article VIII's "Repository status" line.
  3. Optionally, add one clause to Article I distinguishing "conceptual schema design (Level 5)" from "implemented database schema (Level 6)" so the word "schema" is never ambiguous again.
- **Architectural impact:** none on GRAPH/SCHEMA.md's actual content — this is status text only. It removes a real risk that a future reader (human or AI, per Article III Rule 3) misjudges what has and hasn't been ratified, in either direction: overestimating readiness (skipping straight to implementation) or underestimating it (re-doing design work that already exists).
- **Scientific impact:** indirect but real. Scientific Constitution Before Code (VISION.md Article IX) depends on everyone correctly perceiving the boundary between "ratified design" and "authorized implementation" at all times — a stale status statement blurs exactly that boundary, in the same family of error (though far lower stakes) as the evidence-tier blurring VISION.md Article VIII forbids.
- **Long-term impact:** left uncorrected, "Current State" sections drift further from reality every time a new GRAPH/, DATA/, AI/, etc. document is added, compounding across 2,000 phases of intended lifespan. Fixing it now, and making status accuracy a standing Audit-stage check (per the new governance pipeline), prevents recurrence rather than requiring a one-time fix that decays again.
- **Constitutional justification:** MASTER_CONTEXT.md Article III Rule 2 ("Fixing a typo or broken link is not an amendment; changing what a rule means is" — a factual status update falls on the non-amendment side of this line); VISION.md Article V Rule 4 (reproducibility depends on accurate records of what state the system is actually in).
- **Classification:**
  - README.md / Article VIII correction: **Editorial** (factual status correction; no rule's meaning changes).
  - Optional Article I "schema" disambiguation clause: **Architectural** (clarifies a structural definition that other documents rely on).

---

## R2 — GRAPH/SCHEMA_DECISIONS.md internal conflict: D4 and D5 both claim top DEFER priority (Audit Finding 1.2)

- **Problem:** D4's Risk and Future Phase fields both claim priority "if Phase 2 groundwork starts before other domain gaps are filled" / "if Phase 2 work starts first" (conditional). D5's Future Phase field claims, unconditionally, to be "the highest-priority DEFER item among D1–D5." The two claims are not explicitly reconciled anywhere in the document, and the Decision Summary table surfaces neither, flattening both to "Phase 1 (opportunistic)."
- **Affected constitutional articles:** none directly — GRAPH/SCHEMA_DECISIONS.md is a Level-5 governance artifact, not itself constitutional. Indirectly engaged: MASTER_CONTEXT.md Article III Rule 3 (reasoning must be visible and unambiguous to a future reader with no memory of how the document was produced) and VISION.md Article IX (long-horizon clarity, applied here by analogy since the same discipline that protects the constitution should protect its own governance artifacts).
- **Affected documents:** GRAPH/SCHEMA_DECISIONS.md only — specifically the D4 and D5 sections and the Decision Summary table.
- **Smallest possible correction:** add one reconciling sentence, e.g. to D5's Risk field: *"D5 is the default highest-priority DEFER item among D1–D5; D4 supersedes it only in the specific case that Phase 2 groundwork begins before any D-series gap is addressed."* No ACCEPT NOW / DEFER / REJECT classification changes. No other field needs editing.
- **Architectural impact:** none on GRAPH/SCHEMA.md's entity model — this is a sequencing clarification among items that are all currently deferred, not a structural change to the graph.
- **Scientific impact:** minimal directly (no evidence-tier or entity-identity mechanism is touched), but prevents inconsistent, ad hoc prioritization decisions by different future contributors filling D-series entity-coverage gaps opportunistically, which is exactly the kind of quietly-diverging practice the constitution's governance discipline exists to prevent.
- **Long-term impact:** low severity at the current scale (five DEFER items), but the same failure pattern — two priority claims coexisting unreconciled in a governance log — could recur at far larger scale in later phases' own decision logs if not corrected here and named as a discipline now. Fixing it establishes the precedent that decision logs must explicitly reconcile competing priority claims, not just record them side by side.
- **Constitutional justification:** MASTER_CONTEXT.md Article III Rule 3 (visible, unambiguous reasoning for future readers, applied to design-level governance documents by the same logic that binds the constitution itself); VISION.md Article IX ("Build for 2,000 phases" — many future readers will consult this log without this conversation's context).
- **Classification:** **Editorial** (adds one clarifying sentence; changes no ACCEPT/DEFER/REJECT classification and no constitutional meaning).

---

## R3 — The governance pipeline (and its seven-document consultation order) has no ratified home (Audit Finding 4.2)

- **Problem:** the requirement to consult seven specific documents before architectural decisions, and now the full ten-stage governance pipeline (Constitution → Architecture → Review → Decision → Audit → Remediation → Approval → Implementation → Validation → Release), exist only in this conversation. Per MASTER_CONTEXT.md Article III Rule 3, a rule is not truly binding on a future maintainer — human or AI — who has no memory of this conversation and starts only from the repository's files. Separately, the consultation order as originally stated does not match Article I's actual precedence order (Vision → Master Context → Roadmap → README), risking future conflation of "what to read first" with "what wins in a conflict" if the distinction is never written down.
- **Affected constitutional articles:** MASTER_CONTEXT.md Article I (Authority Hierarchy — must stay the sole source of precedence; the pipeline must not be read as altering it), Article III (Governance & Amendment Process — Rule 2 explicitly classifies any change to "Governance itself" as an amendment, which this is), Article IV (this document's existing role of "elaborating VISION.md Article IX for operational use" — the natural home for the pipeline), Article VII (Decision Principles — thematically adjacent, not required to change).
- **Affected documents:** MASTER_CONTEXT.md (the only document that needs to change). VISION.md, ROADMAP.md, and README.md do not require changes — see the companion proposal below for why.
- **Smallest possible correction:** this finding cannot be closed with an editorial tweak. Per Article III Rule 2, formalizing "Governance itself" requires the full amendment process (explicit rationale, Amendment Log entry, version bump). The smallest form of that amendment is exactly two edits to MASTER_CONTEXT.md: (a) one new article defining the ten-stage pipeline, explicitly scoped as elaborating VISION.md Article IX and explicitly not altering Article I's precedence order or ROADMAP's phase sequencing; and (b) one clause added to Article I's Level 5 description naming Review/Decision/Audit/Remediation/Approval artifacts as peers of phase design documents at Level 5 (this also closes Audit Finding 4.1 as a byproduct). The full proposed text is in [DOCS/GOVERNANCE_PIPELINE_AMENDMENT_PROPOSAL.md](GOVERNANCE_PIPELINE_AMENDMENT_PROPOSAL.md).
- **Architectural impact:** turns tacit practice into a citable, checkable rule. Directly closes Audit Finding 5.3 (no enforcement artifact for the consultation requirement) as a side effect — a ratified article is itself the enforcement artifact a future reader can be pointed to, rather than a one-off instruction that only this session remembers.
- **Scientific impact:** this is the highest-leverage fix of the three. The discipline that produced ARCHITECTURE_AUDIT.md itself — constitution before architecture, review before decision, decision before audit, audit before remediation, remediation before approval, approval before implementation — currently only binds this conversation. Ratifying it guarantees it binds every future phase's science, protecting the Evidence Model's tier separation (VISION.md Article VIII) from being bypassed under future time pressure by a contributor who never saw this exchange.
- **Long-term impact:** without ratification, nothing prevents a future session — with no memory of this conversation — from skipping straight to implementation on Phase 2 or beyond. With it, the discipline is self-enforcing across the full 2,000-phase horizon VISION.md Article IX asks XERDNA to be built for, rather than contingent on any one conversation's participants remembering to apply it.
- **Constitutional justification:** VISION.md Article IX (Scientific Constitution Before Code — the pipeline is its most concrete operational expression to date); MASTER_CONTEXT.md Article IV (already exists to elaborate Article IX operationally — this is squarely its job); MASTER_CONTEXT.md Article III (the amendment process this fix must itself go through, which is why it cannot be applied silently even by this Board).
- **Classification:** **Constitutional** (per Article III Rule 2, a change to Governance itself; requires the full amendment process, not an editorial or purely architectural fix).

---

## Summary

| ID | Finding | Smallest correction | Documents touched | Classification |
|---|---|---|---|---|
| R1 | Stale current-state text; ambiguous "schema" | Reword two status statements; optionally disambiguate Article I | README.md, MASTER_CONTEXT.md | Editorial (+ Architectural for the optional clause) |
| R2 | SCHEMA_DECISIONS D4/D5 priority conflict | One reconciling sentence | GRAPH/SCHEMA_DECISIONS.md | Editorial |
| R3 | Governance pipeline unratified | New MASTER_CONTEXT article + one Article I clause | MASTER_CONTEXT.md | Constitutional |

**No document has been modified by this plan.** R1 and R2 can be applied as soon as they are authorized — neither requires the Article III process. R3 requires that process to complete first; its exact proposed text is the subject of the companion document, [DOCS/GOVERNANCE_PIPELINE_AMENDMENT_PROPOSAL.md](GOVERNANCE_PIPELINE_AMENDMENT_PROPOSAL.md).
