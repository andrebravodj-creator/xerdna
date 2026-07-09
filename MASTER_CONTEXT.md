# MASTER CONTEXT

**This is a constitutional document — the operating contract of XERDNA.** Anyone or anything working in this repository — human contributor or AI agent — reads this file first. It carries the highest operational authority of the four constitutional documents; see Article I.

## Article I — Authority Hierarchy

XERDNA's governance rests on a strict hierarchy. When documents or decisions conflict, the higher level wins:

1. **VISION.md** — mission, philosophy, and principle. Wins on questions of intent, ethics, and "why."
2. **MASTER_CONTEXT.md** (this document) — operating law. Wins on questions of "what is and isn't allowed," governance, and structure.
3. **ROADMAP.md** — sequencing. Wins on questions of "what comes next" and "what depends on what."
4. **README.md** — orientation. Never authoritative on its own; it only points to the other three.
5. **Phase-specific design documents, and the governance artifacts that examine them** (e.g. `GRAPH/SCHEMA.md`, and its Review, Decision, Audit, Remediation, and Approval documents per Article XII) — technical designs for a specific phase, and the process artifacts that critique, triage, audit, and gate them. All are peers at this level. Must be traceable to an article in documents 1–3. If any of them conflicts with the constitution, it is wrong and is revised.
6. **Implementation** (code, schemas, infrastructure) — the lowest authority. It implements what the documents above already decided. Per VISION.md Article IX, no implementation is authoritative until it traces back to a ratified article above it.

Nothing below a given level may override it. A technical convenience never outranks a constitutional principle.

## Article II — Non-Negotiable Rules

These hold regardless of phase, component, or how much pressure there is to ship:

1. **Three-tier evidence model, always.** Every biological claim XERDNA surfaces is exactly one of Established Evidence, Computational Prediction, or Research Hypothesis (VISION.md Article IV). If a piece of data cannot be tagged with one of these tiers and its provenance, it does not enter the system.
2. **Never claim discoveries.** XERDNA generates hypotheses and surfaces evidence. It does not assert that something has been discovered, proven, or confirmed.
3. **Assist, never replace.** XERDNA accelerates researchers. It does not substitute for laboratory validation, peer review, or scientific judgment at any phase.
4. **Build for 2,000 phases, not the next 20** (VISION.md Article IX). Architectural decisions on load-bearing components are made as if they must support hundreds of future phases built by people not currently in the room.
5. **Scientific Constitution Before Code** (VISION.md Article IX). No schema, database, ingestion pipeline, API, backend, or interface is treated as authoritative until it is traceable to a ratified constitutional article. Constitutional gaps are resolved by amendment (Article III below), not by quietly building around them.
6. **Biosecurity and ethics are absolute** (VISION.md Article VII). No commercial, technical, or competitive consideration ever outranks the ethical principles.

## Article III — Governance & Amendment Process

XERDNA's constitutional documents (VISION.md, MASTER_CONTEXT.md, ROADMAP.md, README.md) are treated as durable, not disposable — they are not edited casually to justify whatever was just built.

1. **Who may amend:** the founding architect of XERDNA (currently its sole author), or whoever holds that role as the project grows. Delegation of amendment authority is itself a constitutional change and must follow this same process.
2. **What counts as an amendment:** any change to Mission, Vision, Philosophy, Scientific/AI/Evidence/Ethical Principles, Governance itself, Long-Term Architecture Philosophy, Design Rules, Phase Structure, or Naming Conventions. Fixing a typo or broken link is not an amendment; changing what a rule means is.
3. **Process:** an amendment is proposed with its rationale stated explicitly (why the existing text is insufficient, not just what should change), recorded in the Amendment Log (Article XI), and given a version bump. Silent edits to constitutional meaning are not permitted — the reasoning must be visible to whoever reads the document next, including a future XERDNA maintainer with no memory of this conversation.
4. **Conflict resolution between constitutional documents:** VISION.md wins on intent and philosophy; this document wins on everything operational (Article I).
5. **Technical work never amends the constitution implicitly.** If an implementation reveals that a constitutional rule is unworkable, that is a signal to open an amendment — not license to violate the rule in practice while leaving the text unchanged.

## Article IV — Long-Term Architecture Philosophy

Elaborating VISION.md Article IX for operational use:

- New data types, organisms, and evidence modalities must be addable without rewriting what already exists — extension over replacement.
- Provenance and traceability are prioritized over short-term convenience on every load-bearing component.
- Load-bearing components — the knowledge graph, the evidence model, the provenance layer, entity identity — default to boring, well-understood foundations (established standards) over novel, clever ones that are hard to migrate away from.
- No phase's design optimizes for its own use case at the expense of the platform's ability to become the next phase's foundation.
- This standard applies to foundations, not to every feature — a bug fix remains a bug fix.

## Article V — Design Rules

These generalize across every future phase, independent of any specific technology choice:

1. **Typed, never ad hoc.** Every entity and relationship has a defined type. An untyped or "misc" record is a signal that the type system needs a reviewed extension, not a workaround.
2. **Provenance is mandatory, not optional metadata.** Anything without a traceable source and evidence tier is rejected at the boundary where it would enter the system.
3. **Extend by subtyping, not by parallel invention.** When an existing standard or prior XERDNA type almost fits, it is extended or subtyped — not duplicated under a new, competing vocabulary.
4. **Prefer standards the field already converged on** over inventing new ones, for anything load-bearing (Article IV).
5. **Reversibility is a design criterion.** Where two designs solve a problem equally well, the one that is easier to migrate away from later is preferred.

## Article VI — Naming Conventions

1. **Constitutional documents** live at the repository root, in `UPPER_SNAKE_CASE.md`: `README.md`, `MASTER_CONTEXT.md`, `VISION.md`, `ROADMAP.md`.
2. **Top-level repository folders** are `UPPER_CASE` nouns naming a domain of work, not an implementation detail (`GRAPH/`, `DATA/`, `KNOWLEDGE/`, `AI/`, `BACKEND/`, `FRONTEND/`, `RESEARCH/`, `DOCS/`) — see Article IX.
3. **Phase-specific design documents** live inside the folder they belong to (e.g. `GRAPH/SCHEMA.md`) and must open with a pointer back to the constitutional article that authorizes them.
4. **Internal entity identity** uses a namespaced identifier scheme (an `xerdna:` namespace over externally-sourced records) — the concrete instantiation of this principle is a technical design and lives in the relevant phase's design document, not here; this article only fixes the principle that identity is always namespaced and never ad hoc.

## Article VII — Decision Principles

Before any future decision — technical, product, or organizational — is treated as settled, it should answer:

1. Can this be traced back to a specific article in VISION.md or this document? If not, it is not yet authorized (Article II, Rule 5).
2. Does it preserve the separation between Established Evidence, Computational Prediction, and Research Hypothesis in every surface it touches?
3. Is it reversible? If not, does the irreversibility genuinely warrant it (Article IV, V)?
4. Does it favor an existing, well-understood standard over a novel invention, for anything load-bearing?
5. Does it violate any ethical or biosecurity principle in VISION.md Article VII, under any framing? If yes, it is rejected regardless of other merits.
6. Would this decision still make sense if XERDNA is still operating in 50 years, under stewards not yet involved today?

## Article VIII — Current State

- **Phase:** Phase 1 of the Roadmap — Universal Biological Memory (foundational stage).
- **Repository status:** ratified constitutional documentation and Phase 1 conceptual architecture (GRAPH/SCHEMA.md and its governance artifacts). No implementation — database, ingestion pipeline, API, backend, or frontend code — has been authorized yet.
- Full phase sequencing: [ROADMAP.md](ROADMAP.md).

## Article IX — Repository Structure

The top-level layout mirrors where each phase's work will eventually live. Folders exist now as placeholders; they remain empty until the corresponding work is both authorized by the constitution and reached in sequence.

| Folder | Purpose | Primarily serves |
|---|---|---|
| `GRAPH/` | The biological knowledge graph itself — entities, relationships, schema | Phase 1 |
| `DATA/` | Ingestion, connectors to public biological databases and literature | Phase 1 |
| `KNOWLEDGE/` | Curated knowledge base, ontologies, the evidence-tier taxonomy | Phase 1–2 |
| `AI/` | Reasoning engine, hypothesis engine, autonomous research logic | Phase 2, 3, 5 |
| `BACKEND/` | Services, APIs, orchestration across the platform | All phases |
| `FRONTEND/` | Researcher-facing interface, visualization, simulator UI | Phase 4 and onward |
| `RESEARCH/` | Internal R&D, experiment logs, exploratory work not yet productized | All phases |
| `DOCS/` | Documentation beyond the four constitutional documents | All phases |

## Article X — How the Constitutional Documents Fit Together

**Note on ordering:** the list below is expository — the order a new reader would naturally approach the documents to build understanding (orientation, then why, then what/when, then operating law). It is not a restatement of precedence. Precedence between documents in a conflict is decided exclusively by Article I's Authority Hierarchy, which ranks them VISION.md, then this document, then ROADMAP.md, then README.md — a different order than the list below, deliberately, because the two lists answer different questions ("what order should I read these in" versus "which one wins in a conflict").

- **README.md** — entry point: what XERDNA is, current status, where to go next. Not independently authoritative (Article I).
- **VISION.md** — the *why*: mission, origin, scientific/AI/ethical principles, the permanent architectural rules.
- **ROADMAP.md** — the *what and when*: phase sequencing, each phase's objective and constraints.
- **MASTER_CONTEXT.md** (this document) — the *operating law*: authority hierarchy, non-negotiable rules, governance, design rules, current state, repository structure.

## Article XI — Amendment Log

| Version | Date | Change | Rationale |
|---|---|---|---|
| 1.0 | 2026-07-09 | Initial ratification of the constitutional foundation (README, MASTER_CONTEXT, VISION, ROADMAP) | Establish permanent mission, principles, and governance before any schema, ingestion, API, or backend design proceeds — architecture and implementation must trace back to a ratified constitution, not precede it. |
| 1.1 | 2026-07-09 | Added Article XII (Phase Governance Pipeline); amended Article I Level 5 to include review/decision/audit/remediation/approval artifacts as peers of phase design documents | Formalize the ten-stage gate sequence (Constitution → Architecture → Review → Decision → Audit → Remediation → Approval → Implementation → Validation → Release) already applied in practice to Phase 1's GRAPH/ work, so it binds every future phase and every future reader — including one with no memory of the session in which this practice was first established — per Article III Rule 3. |

## Article XII — Phase Governance Pipeline

Elaborating VISION.md Article IX for operational use, in the same manner as Article IV: every phase's work moves through the following gates, in order, before any stage of it is authoritative:

1. **Constitution** — the ratified constitutional documents (VISION.md, this document, ROADMAP.md) that all subsequent work must trace back to (Article I, Article II Rule 5).
2. **Architecture** — a phase-specific design document (Level 5, Article I) proposing a technical model for a ratified constitutional objective.
3. **Review** — a critique of that design document against the constitution, recording findings and severities without modifying the design document itself.
4. **Decision** — a classification of every review finding as ACCEPT NOW, DEFER, or REJECT, each with a stated rationale, impact, risk, dependency, constitutional justification, and owning phase.
5. **Audit** — a cross-document consistency check across the constitution and the phase's architecture, review, and decision documents, surfacing contradictions, circular dependencies, duplicated concepts, missing constitutional references, and architectural weaknesses.
6. **Remediation** — a plan addressing every finding the Audit rates at the severity this document or a future amendment designates as blocking, without yet modifying any document.
7. **Approval** — an explicit, single-valued decision — APPROVED or NOT APPROVED — on whether the phase may proceed to Implementation, stating constitutional, architectural, scientific, and governance readiness, and every unresolved blocker.
8. **Implementation** — code, schemas, infrastructure (Level 6, Article I), built only after Approval, and only to the extent of what was approved.
9. **Validation** — verifying the implementation matches the approved design and every constraint in the constitutional documents it traces to.
10. **Release** — the validated implementation is made available for use.

No stage may be skipped. No phase may enter Implementation while any blocking finding from its own Audit stage remains unresolved (Article II Rule 5).

This article governs *when* a document's contents may be acted on. It does not alter the Authority Hierarchy (Article I) — precedence between documents in a conflict is, and remains, decided by Article I alone, never by a document's position in this pipeline. It does not alter ROADMAP.md's phase sequencing (ROADMAP Article I) — this pipeline governs the gates within a single phase's own work; ROADMAP governs the order phases are taken up across the platform's lifetime. The two are independent axes and neither substitutes for the other.
