# ARCHITECTURE AUDIT

**Status:** Governance report, not implementation. This document does not modify README.md, MASTER_CONTEXT.md, VISION.md, ROADMAP.md, GRAPH/SCHEMA.md, GRAPH/SCHEMA_REVIEW.md, or GRAPH/SCHEMA_DECISIONS.md. It changes nothing automatically. It is the final approval gate before any implementation work begins — findings here should be resolved, explicitly deferred, or explicitly rejected (in the same ACCEPT NOW / DEFER / REJECT form GRAPH/SCHEMA_DECISIONS.md already uses) before `DATA/`, `AI/`, `BACKEND/`, `FRONTEND/`, or `KNOWLEDGE/` work begins.

**On its own place in the hierarchy:** this document deliberately does not self-assign a level in MASTER_CONTEXT.md Article I. Finding 4 below is that Article I has no defined category for meta-documents — reviews, decision logs, audits — that examine other documents rather than proposing a phase's technical design. Until that gap is closed, this report treats itself as informal input to whoever holds amendment authority, not as a ranked artifact in the hierarchy.

**Scope:** all seven documents now required for consultation before architectural decisions, per this session's instruction:

1. The constitutional foundation collectively (README.md, MASTER_CONTEXT.md, VISION.md, ROADMAP.md)
2. MASTER_CONTEXT.md
3. ROADMAP.md
4. VISION.md
5. GRAPH/SCHEMA.md
6. GRAPH/SCHEMA_REVIEW.md
7. GRAPH/SCHEMA_DECISIONS.md

**Method:** each document was read in full and cross-checked against every other document for contradictions, circular dependencies, duplicated concepts, missing constitutional references, and architectural weaknesses. Findings are rated `High` / `Medium` / `Low` and grouped by category, followed by a summary table. A finding being listed here does not mean it is wrong to leave as-is — several are informational or intentional-by-design and are marked as such.

---

## 1. Contradictions

### 1.1 — Stale "Current State" claims vs. the actual existence of GRAPH/SCHEMA.md — **High**

- **Where:** README.md "Status" section ("This repository currently contains constitutional and structural documentation only. No application code, schema, or implementation has been authorized yet.") and MASTER_CONTEXT.md Article VIII ("Repository status: constitutional and structural documentation only. No application code, schemas, or implementation has been authorized yet.").
- **The contradiction:** both sentences assert no schema has been authorized. But GRAPH/SCHEMA.md exists, is a substantive conceptual design (not a placeholder), opens with an explicit constitutional-basis citation, and is now further elaborated by GRAPH/SCHEMA_REVIEW.md and the just-ratified GRAPH/SCHEMA_DECISIONS.md. Taken literally, "no schema... has been authorized yet" is false as of this audit.
- **Root cause:** the word "schema" is used in two senses that MASTER_CONTEXT.md Article I never disambiguates. Article I Level 5 gives `GRAPH/SCHEMA.md` — a *conceptual* design document — as its own example of a "phase-specific design document." Article I Level 6 ("Implementation") separately lists "code, schemas, infrastructure," meaning *implemented* (e.g., DDL/database) schemas. Article VIII's "no... schemas... authorized yet" reads naturally as a Level-6 claim (no database schema exists), which is still true — but the sentence doesn't say that, and a reader who doesn't already know the Level 5/6 distinction will reasonably read it as false.
- **Compounding ambiguity:** ROADMAP.md Article I states a phase is "reached" once "its technical designs trace back to ratified constitutional articles" — not once implementation exists. GRAPH/SCHEMA.md explicitly traces to ratified articles. By ROADMAP's own test, Phase 1's foundational design work has arguably already been "reached" in a conceptual sense, which the "documentation only" framing in README/MASTER_CONTEXT Article VIII does not reflect.
- **Recommendation (not applied here):** update README.md "Status" and MASTER_CONTEXT.md Article VIII to state plainly that conceptual/architectural design work for Phase 1 (SCHEMA.md, SCHEMA_REVIEW.md, SCHEMA_DECISIONS.md) exists and is ratified, while implementation (database, ingestion code, API, application code) remains unauthorized. This is a factual status update, not a change to Mission/Vision/Philosophy/Principles/Governance/Architecture Philosophy/Design Rules/Phase Structure/Naming Conventions — so per Article III Rule 2 it does not require the full amendment process.

### 1.2 — Internal inconsistency in GRAPH/SCHEMA_DECISIONS.md: two items both claim top DEFER priority — **High**

- **Where:** GRAPH/SCHEMA_DECISIONS.md, D4 and D5.
- **The contradiction:** D4's Risk line says: *"Worth prioritizing this DEFER item first among D1–D5 if Phase 2 groundwork starts before other domain gaps are filled"* and its Future Phase line says *"prioritize ahead of D1/D2/D3/D5 if Phase 2 work starts first."* D5's Future Phase line says, unconditionally: *"flagged as the highest-priority DEFER item among D1–D5."* Read together, it is unclear whether D4 or D5 is the standing top-priority DEFER item — D5's claim is unconditional and D4's is conditional, but the document never reconciles them, and the Decision Summary table at the top flattens both to a plain "Phase 1 (opportunistic)" with no indication either is more urgent than the other three.
- **Why this matters now:** per this session's instruction, GRAPH/SCHEMA_DECISIONS.md is approved architecture governance and one of the seven documents every future phase must consult before architectural decisions. An unresolved priority conflict inside an approved governance document will propagate into real sequencing decisions (e.g., someone implementing D4's macromolecular complex type believing it's unconditionally top priority, when D5's population/cohort entity carries the higher stated risk rating of the two).
- **Recommendation:** add one reconciling sentence — e.g., "D5 is the default highest-priority DEFER item; D4 supersedes it only if Phase 2 groundwork begins before any D-series gap is addressed" — as a targeted edit to GRAPH/SCHEMA_DECISIONS.md, following the same edit discipline SCHEMA_DECISIONS itself prescribes for SCHEMA.md (explicit, traceable, not silent).

---

## 2. Circular Dependencies

### 2.1 — A Level-5 document's own text used as partial "constitutional justification" for a decision about itself — **Medium**

- **Where:** GRAPH/SCHEMA_DECISIONS.md, R2 ("Entity split/merge lineage").
- **The pattern:** R2's constitutional justification field cites two things jointly: "VISION.md Article IX" (a genuine constitutional citation) and "the Entity Identity section's own stated stakes" — i.e., a sentence from GRAPH/SCHEMA.md itself ("get identity wrong and every later phase inherits silent duplication or silent conflation"). MASTER_CONTEXT.md Article I is explicit that Level-5 documents "must be traceable to an article in documents 1–3" and that "if a design document conflicts with the constitution, the design document is wrong and is revised" — the hierarchy is designed to run one direction (constitution authorizes design), not for a design document to co-justify decisions about its own content by quoting itself.
- **Severity note:** this is not a hard circularity (SCHEMA.md's own stakes-statement is itself traceable back to VISION.md Article IX/MASTER_CONTEXT.md Article IV, so the reasoning doesn't loop indefinitely) — but citing it under the heading "constitutional justification" blurs Article I's category boundary between constitutional authority (Levels 1–3) and design-level rationale (Level 5).
- **Recommendation:** in any future revision of GRAPH/SCHEMA_DECISIONS.md, keep design-document self-references in the "Why" field (where they already appear appropriately elsewhere in the document) and reserve "Constitutional justification" strictly for citations to VISION.md / MASTER_CONTEXT.md / ROADMAP.md.

### 2.2 — Overlapping phases are explicit and intentional, not a defect — **Informational, no action**

- ROADMAP.md Article I states Phase 2 "cannot mature without Phase 1 already growing" and that "Phase 1 never actually finishes." This looks superficially like a circular dependency (Phase 2 depends on Phase 1, which never completes, so Phase 2 never starts) but ROADMAP.md itself disclaims this reading directly: "Treat phase boundaries as centers of gravity, not hard gates," consistent with VISION.md Article III ("XERDNA is not done at any named phase"). Verified consistent — recorded here only so this audit's coverage of "circular dependencies" is seen to be complete, not overlooked.

---

## 3. Duplicated Concepts

### 3.1 — Extensibility Rule stated three times within GRAPH/SCHEMA.md — **Low**

- The "check Biolink/OBO first, then subtype under `xerdna:`, never mint an untyped node" rule appears near-verbatim in the "Foundational Choice" closing paragraph, in its own dedicated "Extensibility Rule" section, and again in the "Namespace Registry" section's governance clause. Not a contradiction — all three statements agree — but it is the same content restated three times in one document, which is a mild irony given the rule itself (MASTER_CONTEXT.md Article V Rule 3) is "extend by subtyping, not by parallel invention." Cosmetic; worth consolidating to a single canonical statement with the other two sections referencing it, next time SCHEMA.md is edited for other reasons.

### 3.2 — Two different predicate names for the same "uncertain identity" pattern — **Low, forward-looking**

- GRAPH/SCHEMA.md's Entity Identity section defines `xerdna:possibly_same_as` for unresolved entity-identity ambiguity. GRAPH/SCHEMA_REVIEW.md finding H3 (accepted as DEFER, owned by Phase 3 in SCHEMA_DECISIONS.md) proposes extending "the same pattern" to hypothesis deduplication via a *differently named* predicate, `xerdna:possibly_duplicate_of`. These are conceptually the same pattern (don't silently merge below a certainty threshold; record the ambiguity as a first-class relationship instead) applied to two record types. Not a current inconsistency — H3 hasn't been designed yet — but when Phase 3 does design it, the Namespace Registry should document both predicates under one named pattern so they don't drift into two independently-invented conventions for the same idea.

### 3.3 — "Build for 2,000 phases" / "Scientific Constitution Before Code" restated across README, VISION, MASTER_CONTEXT — **Informational, no action**

- Both permanent rules are stated in full in three or four places (README Guiding Principles, VISION.md Article IX, MASTER_CONTEXT.md Article II Rules 4–5 and Article IV). This reads as intentional emphasis of the two permanent rules across every constitutional document a reader might open first, consistent with MASTER_CONTEXT.md Article X's description of how the four documents "fit together." Recorded for completeness; not a defect.

---

## 4. Missing Constitutional References

### 4.1 — MASTER_CONTEXT.md Article I has no hierarchy level for review or decision/governance documents — **Medium**

- Article I defines six levels ending at Level 5 ("phase-specific design documents... e.g. `GRAPH/SCHEMA.md`") and Level 6 ("Implementation"). GRAPH/SCHEMA_REVIEW.md is not a design document — it's a critique of one — yet it self-assigns "Level-5 in the authority hierarchy... same as SCHEMA.md itself," an informal extension of Article I that Article I itself never states. GRAPH/SCHEMA_DECISIONS.md, produced from that review, doesn't self-assign any level at all. The result: two sibling documents in the same folder, produced in immediate succession, classify themselves inconsistently (one claims a level Article I doesn't define; the other claims none).
- **Recommendation:** either (a) propose an Article I amendment adding an explicit category for review/decision/audit documents (with its own stated precedence relative to Level 5), following the Article III process with a stated rationale, or (b) at minimum, have GRAPH/SCHEMA_REVIEW.md and GRAPH/SCHEMA_DECISIONS.md agree on and state the same self-classification. This report (Section header above) intentionally avoids self-assigning a level for the same reason.

### 4.2 — This session's seven-document consultation order exists nowhere in a ratified document — **High**

- The instruction "every future phase must consult [these seven documents] before making architectural decisions" was given verbally this session. It is not recorded in MASTER_CONTEXT.md, VISION.md, ROADMAP.md, or README.md. MASTER_CONTEXT.md Article III Rule 3 requires that constitutional reasoning "be visible to whoever reads the document next, including a future XERDNA maintainer with no memory of this conversation" — by that standard, a rule that exists only in this chat transcript does not yet bind a future session, human or AI, that starts from the repository files alone.
- **A second, sharper issue:** the consultation order as given — Constitution, Master Context, Roadmap, Vision, Schema, Schema Review, Schema Decisions — does not match MASTER_CONTEXT.md Article I's ratified precedence order, which is Vision → Master Context → Roadmap → README (Levels 1–4), then Schema-level documents. Consultation order (what to read first) and precedence order (what wins in a conflict) are legitimately different things, but nowhere is that distinction stated, so a future reader could easily conflate "consult in this order" with "this is now the precedence order," effectively misreading Article I by implication.
- **A third issue, minor:** the consultation order's first item, "Constitution," is not one of the four named constitutional documents (README, MASTER_CONTEXT, VISION, ROADMAP per README's own table and MASTER_CONTEXT Article X) — it isn't clear whether "Constitution" here means README.md specifically (the closest thing to a single entry point) or the four-document set collectively, in which case it redundantly re-lists three of its own members as separate subsequent steps (Master Context, Roadmap, Vision).
- **Recommendation:** if this consultation order is meant to persist beyond this session, it belongs in MASTER_CONTEXT.md — the operating-law document — as an explicit addition (e.g., a new article or a rule under Article VII, Decision Principles), written through the Article III process with its rationale, and worded to make clear it governs *reading order*, not *conflict precedence* (which Article I already owns and is unchanged).

### 4.3 — ROADMAP.md Article II's Phase 1 entity list vs. GRAPH/SCHEMA.md's added entity types — **Medium**

- ROADMAP.md Article II (Level 3, "wins on... what depends on what" per Article I) enumerates a specific Phase 1 entity list that does not include disease, phenotype, or anatomy. GRAPH/SCHEMA.md (Level 5) adds `biolink:Disease`, `biolink:PhenotypicFeature`, and `biolink:AnatomicalEntity` anyway, citing MASTER_CONTEXT.md Article IV (Level 2, general extensibility philosophy) as its justification, and states this explicitly rather than silently. This is not a violation — SCHEMA.md is transparent about the addition and its rationale — but it is a Level-5 document using a Level-2 general principle to expand a Level-3 document's specific, named scope list, without the addition appearing in ROADMAP.md itself. Given Article I's stated purpose (higher levels win when documents conflict), it's worth being explicit about whether "Article IV can be used to enlarge ROADMAP's own itemized list without touching ROADMAP" is the intended reading, or whether ROADMAP.md Article II should simply be updated to name these three categories directly the next time ROADMAP is revisited.

---

## 5. Architectural Weaknesses

### 5.1 — One-directional traceability between GRAPH/SCHEMA.md and its own review/decisions — **Medium**

- GRAPH/SCHEMA_REVIEW.md and GRAPH/SCHEMA_DECISIONS.md both open by pointing back to GRAPH/SCHEMA.md. GRAPH/SCHEMA.md itself contains no forward reference to either — a reader who opens only SCHEMA.md has no way to discover that a review exists, that 14 findings have been accepted against it, or that a decisions log governs what happens next. This breaks the traceability chain the constitution treats as load-bearing (VISION.md Article V Rule 4; MASTER_CONTEXT.md Article V Rule 2) at the one place readers are most likely to start.
- **Compounding gap:** GRAPH/SCHEMA_DECISIONS.md's own R1 (accepted) proposes a `schema_version` field plus "a schema-level changelog, distinct from the constitutional Amendment Log" for tracking future SCHEMA.md revisions — but that changelog scaffold doesn't exist yet either, so even once the 14 ACCEPT NOW items are eventually applied to SCHEMA.md, there is currently no defined place to record that they were.
- **Recommendation:** when SCHEMA.md is next revised to incorporate the 14 ACCEPT NOW items, add (a) a short forward-pointer near the top of SCHEMA.md to SCHEMA_REVIEW.md and SCHEMA_DECISIONS.md, and (b) the schema-level changelog R1 already calls for, so the traceability chain runs both directions.

### 5.2 — Single-point-of-failure in amendment authority — **Low, forward-looking**

- MASTER_CONTEXT.md Article III Rule 1 vests amendment authority in "the founding architect of XERDNA (currently its sole author)... Delegation of amendment authority is itself a constitutional change." This is reasonable for the project's current stage but sits in tension with Article VII Decision Principle 6, which asks every decision to hold up "under stewards not yet involved today." No succession or continuity mechanism is defined for what happens to amendment authority itself if the sole author is unavailable — not urgent at Phase 1, but worth flagging now precisely because VISION.md Article IX asks load-bearing components to be designed for a 2,000-phase horizon, and governance is as load-bearing as the graph schema.

### 5.3 — No enforcement artifact for the new consultation requirement — **Medium**

- Directly related to Finding 4.2: even if the seven-document consultation order is written into MASTER_CONTEXT.md, nothing in the repository currently checks or reminds a future contributor (human or AI) to actually do it before starting architectural work — there is no checklist, template, or gating document referenced from README.md's entry point. This report itself is one instance of the kind of gate that's currently missing a durable home; without one, the same gap this audit was commissioned to close could silently reopen on the next major decision.

---

## Summary

| # | Finding | Category | Severity |
|---|---|---|---|
| 1.1 | "Current state" text in README/MASTER_CONTEXT is stale; "schema" spans two authority levels without disambiguation | Contradiction | High |
| 1.2 | SCHEMA_DECISIONS D4 and D5 both claim top DEFER priority, unreconciled | Contradiction | High |
| 4.2 | Seven-document consultation order has no ratified home; risks being conflated with Article I's precedence order | Missing reference | High |
| 2.1 | SCHEMA_DECISIONS R2 cites SCHEMA.md's own text as part of "constitutional justification" | Circular dependency | Medium |
| 4.1 | No Article I hierarchy level for review/decision documents; REVIEW and DECISIONS self-classify inconsistently | Missing reference | Medium |
| 4.3 | SCHEMA.md's added entity types (Disease/Phenotype/Anatomy) extend ROADMAP's Level-3 list via a Level-2 principle | Missing reference | Medium |
| 5.1 | SCHEMA.md has no forward link to its own review/decisions; no schema-level changelog yet exists | Architectural weakness | Medium |
| 5.3 | No enforcement artifact for the new consultation requirement | Architectural weakness | Medium |
| 3.1 | Extensibility Rule restated three times within SCHEMA.md | Duplication | Low |
| 3.2 | `possibly_same_as` / `possibly_duplicate_of` — same pattern, two names | Duplication | Low |
| 5.2 | Amendment authority is a single point of failure | Architectural weakness | Low |
| 2.2 | Phase overlap looks circular but is explicitly, correctly disclaimed | Circular dependency | Informational |
| 3.3 | Core permanent rules intentionally restated across constitutional documents | Duplication | Informational |

**3 High, 4 Medium, 3 Low, 2 Informational.**

---

## What This Report Recommends, Not Decides

Per Scientific Constitution Before Code (VISION.md Article IX) and the same governance discipline GRAPH/SCHEMA_DECISIONS.md already applies to itself, this audit classifies nothing as accepted, deferred, or rejected — that is a separate, subsequent step, requiring its own explicit go-ahead, ideally recorded in a companion decisions document the same way SCHEMA_REVIEW.md's findings were triaged into GRAPH/SCHEMA_DECISIONS.md. Until that triage happens, this report stands as the final gate: the three `High` findings — stale current-state claims, the unreconciled D4/D5 priority conflict, and the unrecorded consultation order — are the ones most likely to cause real confusion if implementation work begins before they're resolved.
