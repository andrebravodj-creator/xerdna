# GRAPH SCHEMA DECISIONS

**Status:** Governance record, not implementation. This document classifies every finding in [SCHEMA_REVIEW.md](SCHEMA_REVIEW.md) as **ACCEPT NOW**, **DEFER**, or **REJECT**, per VISION.md Article IX ("Build for 2,000 phases, not the next 20") and Scientific Constitution Before Code. No recommendation classified here is applied to [SCHEMA.md](SCHEMA.md) by this document — a classification of ACCEPT NOW means "this should be incorporated into SCHEMA.md as a documentation edit, in a separate, explicit step," not that it has been. This is architecture governance only.

**How to read a decision:** each finding gets *why* (the reasoning behind the classification itself — not the reasoning behind the finding, which SCHEMA_REVIEW.md already gave), *impact* (what changes if this is adopted, or what continues to be missing if not), *risk* (what residual exposure remains either way), *dependency* (what this decision is contingent on), *constitutional justification* (the specific article grounding the call), and *future phase* (where this is ultimately owned).

---

## Decision Summary

| ID | Finding | Decision | Owning Phase |
|---|---|---|---|
| D1 | Epigenetics entity type | DEFER | Phase 1 (opportunistic) |
| D2 | Expression measurement entity | DEFER | Phase 1 (opportunistic) |
| D3 | Molecular function / reaction entities | DEFER | Phase 1 (opportunistic) |
| D4 | Macromolecular complex type | DEFER | Phase 1 (opportunistic) |
| D5 | Population/cohort entity | DEFER | Phase 1 (opportunistic) |
| D6 | Gene–environment interaction entity | **REJECT** | — |
| E1 | Ingestion-time rubric for `established_evidence` | ACCEPT NOW | Phase 1 (principle now, per-source rubrics ongoing) |
| E2 | Causal vs. correlational qualifier | ACCEPT NOW | Phase 1 |
| E3 | Retraction/supersession lifecycle field | ACCEPT NOW | Phase 1 (field); Phase 5 (active monitoring) |
| E4 | Conflicting `established_evidence` is valid, not an error | ACCEPT NOW | Phase 1 |
| H1 | Prediction → hypothesis promotion boundary | ACCEPT NOW | Phase 1 (rule); Phase 3 (mechanism) |
| H2 | Hypothesis `claim` may span a subgraph | ACCEPT NOW | Phase 1 |
| H3 | Hypothesis deduplication / identity | DEFER | Phase 3 |
| H4 | No hypothesis `status` is permanently terminal | ACCEPT NOW | Phase 1 |
| O1 | Pin Biolink Model / OBO ontology versions | ACCEPT NOW | Phase 1 |
| O2 | Ground `method` in a controlled vocabulary | ACCEPT NOW | Phase 1 (principle); ongoing per-method binding |
| O3 | Chemical identity granularity caveat | ACCEPT NOW | Phase 1 |
| O4 | Adopt Biolink qualifiers for directionality | ACCEPT NOW | Phase 1 |
| P1 | "Checked, absent" representation | ACCEPT NOW | Phase 1 (schema); Phase 2 (consuming index) |
| P2 | `Finding` entity for Phase 2 output | DEFER | Phase 2 |
| P3 | Active graph-staleness tracking | DEFER | Phase 5 |
| R1 | `schema_version` tag on every record | ACCEPT NOW | Phase 1 |
| R2 | Entity split/merge lineage | ACCEPT NOW | Phase 1 |
| R3 | New namespace-registry governance for multi-contributor scale | **REJECT** | — |
| R4 | State the Biolink abstraction boundary explicitly | ACCEPT NOW | Phase 1 |

**15 ACCEPT NOW, 8 DEFER, 2 REJECT.**

---

## 1. Missing Biological Domains

### D1 — Epigenetics entity type — **DEFER**

- **Why:** Not load-bearing. This is breadth-of-coverage, not a change to identity, evidence, or provenance structure — exactly the kind of addition MASTER_CONTEXT.md Article IV already promises can happen "without rewriting what already exists." Adding it now, with no epigenetic data source yet prioritized, is speculative.
- **Impact:** Deferring costs nothing structurally — the Extensibility Rule (check Biolink/OBO first, then `xerdna:` subtype) already covers how this gets added when needed.
- **Risk:** Low. The only risk is if epigenetic data becomes urgent before anyone revisits this — mitigated by it being a cheap, mechanical addition when that happens.
- **Dependency:** A real epigenomics ingestion source being prioritized.
- **Constitutional justification:** MASTER_CONTEXT.md Article IV (extension over speculative pre-building).
- **Future phase:** Phase 1, added opportunistically alongside the source that needs it.

### D2 — Expression measurement entity — **DEFER**

- **Why:** Same reasoning as D1 — an entity-coverage gap, not a structural one.
- **Impact:** None if deferred; the `expressed_in` predicate already exists as a coarser stand-in.
- **Risk:** Low — quantitative expression data ingested before this exists would have to be represented as boolean edges temporarily, a known and reversible simplification.
- **Dependency:** A transcriptomics/expression data source being prioritized.
- **Constitutional justification:** MASTER_CONTEXT.md Article IV.
- **Future phase:** Phase 1, opportunistic.

### D3 — Molecular function / reaction entities — **DEFER**

- **Why:** Same category as D1/D2. GO Molecular Function is an established OBO category, so adopting it later is "use the existing standard" (Extensibility Rule step 1), not invention — there's no cost to waiting.
- **Impact:** Pathway-level data can be ingested now at the coarse grain; reaction-level detail waits.
- **Risk:** Low, and explicitly reversible — adding reaction-level detail under an existing pathway later doesn't require restructuring the pathway entities already ingested.
- **Dependency:** A source providing reaction/enzyme-level detail (e.g., Reactome, KEGG) being prioritized.
- **Constitutional justification:** MASTER_CONTEXT.md Article V Rule 4 (prefer existing standards — GO-MF already exists, no need to design one).
- **Future phase:** Phase 1, opportunistic.

### D4 — Macromolecular complex type — **DEFER**

- **Why:** Same reasoning. Also directly useful to Phase 2 (interaction-network reasoning), but usefulness to a later phase doesn't make it foundational to Phase 1's own correctness.
- **Impact:** Complexes are representable today via multiple pairwise `interacts_with` edges — a real but tolerable simplification, not a data-loss trap (individual interactions are still captured, just not grouped as one addressable complex).
- **Risk:** Low. Worth prioritizing this DEFER item first among D1–D5 if Phase 2 groundwork starts before other domain gaps are filled, since interaction networks are Phase 2's most direct substrate.
- **Dependency:** Protein-protein interaction data ingestion, or early Phase 2 design work, whichever comes first.
- **Constitutional justification:** MASTER_CONTEXT.md Article IV.
- **Future phase:** Phase 1, opportunistic — prioritize ahead of D1/D2/D3/D5 if Phase 2 work starts first.

### D5 — Population/cohort entity — **DEFER**

- **Why:** A real gap, but it is an entity-type addition, not itself a change to how evidence, identity, or provenance work — E2 (causal/correlational qualifier), which is genuinely foundational, can be designed independently of whether a Population entity exists yet.
- **Impact:** Population-scale genomic data (GWAS, allele frequency) can't be represented with its own entity until this is added, but individual `SequenceVariant` records remain valid and useful in the meantime.
- **Risk:** Moderate if deferred too long — population genetics is plausibly within "Genomes" in ROADMAP.md Article II's Phase 1 scope, so this shouldn't be deferred indefinitely, only until a population-scale source is actually being ingested. D5 is the default highest-priority DEFER item among D1–D5; D4 supersedes it only in the specific case that Phase 2 groundwork begins before any D-series gap is addressed.
- **Dependency:** A population/cohort-scale genomic data source (e.g., gnomAD-style) being prioritized; benefits from E2 already being in place.
- **Constitutional justification:** MASTER_CONTEXT.md Article IV; ROADMAP.md Article II (Genomes is named Phase 1 scope).
- **Future phase:** Phase 1, opportunistic — but flagged as the highest-priority DEFER item among D1–D5.

### D6 — Gene–environment interaction entity — **REJECT**

- **Why:** The review's own recommendation was hedged ("flag as a deliberate scope decision if intentional, or add... if not") — a sign the finding itself wasn't confident this needs a dedicated new type. Minting a bespoke `xerdna:` entity for this now, with no concrete data source driving it and no existing Biolink/OBO category confirmed to fit, is exactly the speculative pre-building MASTER_CONTEXT.md Article IV warns against and cuts against Article V Rule 3 (extend by subtyping, not parallel invention) — inventing a type before checking what's actually needed is invention-first, not extension-first.
- **Impact:** Gene-environment relationships remain unrepresented until revisited — an honest gap, not a silently-dropped one now that it's recorded here.
- **Risk:** Low near-term (no current source needs this); if a real exposure-data source is prioritized later, the first step is checking Biolink/OBO for a fitting category before considering a new `xerdna:` type — i.e., redo the Extensibility Rule's step 1 at that time rather than pre-deciding now.
- **Dependency:** None — this is a rejection of premature action, not a rejection of the domain's validity.
- **Constitutional justification:** MASTER_CONTEXT.md Article IV (not a license to over-build speculatively) and Article V Rule 3 (extend by subtyping, not parallel invention).
- **Future phase:** None assigned — revisit only if a concrete exposure/environmental data source is proposed for ingestion, at which point this becomes a fresh D-series finding, not a resumption of this one.

---

## 2. Weak Evidence Handling

### E1 — Ingestion-time rubric for `established_evidence` — **ACCEPT NOW**

- **Why:** This is squarely load-bearing — VISION.md Article VIII treats tier-blurring as the platform's central risk, and without a documented rubric requirement, two ingestion efforts could tier the same kind of record inconsistently from day one. The *requirement* that a rubric must exist is cheap to state now; only the *content* of each source's specific rubric needs a real source to write.
- **Impact:** SCHEMA.md gains a stated rule: every future source design document must include an explicit tiering rubric before ingestion begins. No existing content changes; this closes a gap in what "authoritative source" means.
- **Risk:** If deferred, the first ingestion connector would set an unreviewed precedent for what counts as authoritative — hard to walk back once other sources copy it.
- **Dependency:** None to accept the principle; each source's specific rubric depends on that source being selected for ingestion (Phase 1, ongoing).
- **Constitutional justification:** VISION.md Article VIII; MASTER_CONTEXT.md Article II Rule 1.
- **Future phase:** Phase 1 — the principle now; specific rubrics written source-by-source as `DATA/` connectors are designed.

### E2 — Causal vs. correlational qualifier — **ACCEPT NOW**

- **Why:** This is an Evidence Model expressiveness gap, not an entity-coverage gap — it affects how *every* association is represented, including ones already conceptually defined in SCHEMA.md. Retrofitting a qualifier onto edges ingested without it later would require re-auditing every existing correlational claim to determine which predicate it should have used.
- **Impact:** The Relationship Types section gains a rule: statistically-associated-but-not-causally-established findings default to `correlated_with` (or an equivalent weaker predicate), never a causal predicate, unless the source itself supports causation.
- **Risk:** Low to adopt now; high to defer — this is the textbook "cheap now, expensive after data exists" case the 2,000-phase rule exists to catch.
- **Dependency:** None.
- **Constitutional justification:** VISION.md Article VIII; MASTER_CONTEXT.md Article IV.
- **Future phase:** Phase 1.

### E3 — Retraction/supersession lifecycle field — **ACCEPT NOW**

- **Why:** The *field* (a provenance lifecycle status) is cheap schema work and is exactly the kind of thing that's disproportionately expensive to retrofit — every record ingested before the field exists lacks a slot to ever record a later retraction. The *operational* work of actually monitoring retraction feeds is a different, much larger undertaking that legitimately belongs to a later phase.
- **Impact:** The Provenance Model gains a `status` field (`active` / `retracted` / `superseded_by`), defaulting to `active` at ingestion. No monitoring service is built.
- **Risk:** Without the field now, Phase 5's eventual monitoring work would have nowhere to write its findings without a schema change touching every historical record — the exact retrofit cost this decision avoids.
- **Dependency:** None for the field; the active monitoring mechanism depends on Phase 5 (Autonomous Scientist) being reached.
- **Constitutional justification:** MASTER_CONTEXT.md Article IV; VISION.md Article V Rule 4 (reproducibility depends on knowing a source's current status).
- **Future phase:** Phase 1 (field definition now); Phase 5 (active retraction monitoring, see P3).

### E4 — Conflicting `established_evidence` is valid, not an error — **ACCEPT NOW**

- **Why:** This is a zero-cost documentation clarification with an outsized downside if skipped — without it, a future ingestion implementer could "fix" a conflict by dropping one side, destroying exactly the signal ROADMAP.md Article III's Phase 2 needs to find conflicting evidence.
- **Impact:** SCHEMA.md states explicitly that contradictory `established_evidence` edges between the same nodes are an expected, preserved graph state, not a data-quality error to resolve at ingestion.
- **Risk:** Negligible to adopt; meaningful data loss if deferred and an ingestion engineer makes the opposite assumption first.
- **Dependency:** None.
- **Constitutional justification:** ROADMAP.md Article III; VISION.md Article V Rule 3 (refutation is signal, not noise).
- **Future phase:** Phase 1.

---

## 3. Unclear Hypothesis Boundaries

### H1 — Prediction → hypothesis promotion boundary — **ACCEPT NOW**

- **Why:** This is a boundary-definition problem, not a feature — it costs nothing to write down now and directly protects the Evidence Model's tier separation (VISION.md Article VIII), which is the platform's most load-bearing constraint. Waiting until Phase 3 actually builds the Hypothesis Engine risks that engine's implementers inventing their own inconsistent promotion logic first.
- **Impact:** SCHEMA.md states explicitly: a hypothesis may cite predictions as `supporting_evidence`, but no prediction becomes a hypothesis by confidence threshold alone — only by an explicit reasoning step producing the required `claim`, `contradicting_evidence`, and `reasoning` fields.
- **Risk:** Low to adopt; if deferred, Phase 3 design would start without a stated boundary, and undoing an ad hoc promotion mechanism already in use would be harder than defining the rule first.
- **Dependency:** None for the rule; the actual promotion mechanism's implementation depends on Phase 3.
- **Constitutional justification:** VISION.md Article VIII; ROADMAP.md Article IV.
- **Future phase:** Phase 1 (rule now); Phase 3 (mechanism).

### H2 — Hypothesis `claim` may span a subgraph — **ACCEPT NOW**

- **Why:** Cheap clarification of existing text ("scoped to specific graph entities" is ambiguous, not wrong) — no new mechanism, just removes an ambiguity that could otherwise cause Phase 3 to under-build the `claim` field as strictly pairwise.
- **Impact:** SCHEMA.md's Hypothesis Model clarifies that `claim` may reference an arbitrary set of graph entities/edges, not only a single relationship.
- **Risk:** Negligible either way, but free to fix now.
- **Dependency:** None.
- **Constitutional justification:** ROADMAP.md Article IV (hypotheses often describe mechanisms, not single facts).
- **Future phase:** Phase 1.

### H3 — Hypothesis deduplication / identity — **DEFER**

- **Why:** No hypotheses exist yet to deduplicate — this problem only manifests at the volume Phase 6 (Collective Intelligence, many contributors) introduces. Designing it now, before Phase 3 even produces a hypothesis, risks over-specifying a mechanism before real hypothesis data exists to test it against.
- **Impact:** No cost to deferring — the Entity Identity pattern (`xerdna:possibly_same_as`) already exists as a template to extend when needed.
- **Risk:** Low. The main risk is Phase 3 inventing an inconsistent ad hoc dedup mechanism first — mitigated by flagging this finding now so Phase 3's design explicitly inherits it as a known open item, not a fresh discovery.
- **Dependency:** Phase 3's Hypothesis Engine design; informed by, but not blocking on, Phase 6 contributor volume.
- **Constitutional justification:** MASTER_CONTEXT.md Article IV (extend by subtyping the existing identity pattern, when the time comes).
- **Future phase:** Phase 3.

### H4 — No hypothesis `status` is permanently terminal — **ACCEPT NOW**

- **Why:** Zero-cost clarification directly tied to VISION.md Article III ("XERDNA is not done at any named phase... there is no 'done'"), applied at the hypothesis level. Leaving it unstated risks a future implementation treating `refuted`/`supported_by_experiment` as an immutable end state, which would be inconsistent with the platform's own philosophy.
- **Impact:** SCHEMA.md's Hypothesis Model states explicitly that any `status` value can transition again given new `established_evidence`.
- **Risk:** Negligible to adopt.
- **Dependency:** None.
- **Constitutional justification:** VISION.md Article III.
- **Future phase:** Phase 1.

---

## 4. Ontology Gaps

### O1 — Pin Biolink Model / OBO ontology versions — **ACCEPT NOW**

- **Why:** This is the same "cheap now, expensive after data exists" pattern as E2/R1 — pinning a version costs one line; retroactively figuring out which version a historical mapping assumed, after both the schema and the ontologies have moved on independently for years, may be nearly impossible.
- **Impact:** SCHEMA.md's Foundational Choice section names the specific Biolink Model release and OBO ontology snapshot in use, plus a stated upgrade policy: ontology version upgrades are schema-level decisions requiring a recorded rationale, following the same pattern as the Namespace Registry.
- **Risk:** Low to adopt now; without it, every future reader of an old graph record has to guess which vocabulary version it assumed.
- **Dependency:** None.
- **Constitutional justification:** MASTER_CONTEXT.md Article IV; Article V Rule 4.
- **Future phase:** Phase 1.

### O2 — Ground `method` in a controlled vocabulary — **ACCEPT NOW**

- **Why:** The *principle* (method must not remain indefinitely free text) is foundational to Design Rule 1 (typed, never ad hoc) and costs nothing to state now, with a fallback (`ontology_gap: true`) that doesn't block any current work. The *specific* ontology choice (OBI or an alternative) is exactly the kind of deliberate, standards-first evaluation this project already did once for Biolink/OBO — it deserves its own similarly deliberate pass once real method names are being ingested, not a quick bolt-on now.
- **Impact:** SCHEMA.md's Prediction Model states `method` must bind to a controlled vocabulary term where one exists, with an explicit gap flag when it doesn't — preventing silent free-text sprawl from day one, without forcing a premature ontology commitment.
- **Risk:** Low. The main risk of deferring the specific ontology choice is inconsistent method-naming in the interim — mitigated by the `ontology_gap` flag making every unresolved case visible and auditable rather than silently accumulating.
- **Dependency:** The specific vocabulary decision depends on real method names from the first prediction-generating pipeline.
- **Constitutional justification:** MASTER_CONTEXT.md Article V Rule 1 (typed, never ad hoc); Article V Rule 4 (prefer standards, decided deliberately as Biolink/OBO was).
- **Future phase:** Phase 1 (principle and flag mechanism now); vocabulary binding decided when the first real prediction pipeline exists.

### O3 — Chemical identity granularity caveat — **ACCEPT NOW**

- **Why:** This is an identity-model correctness issue, and the Entity Identity section itself already calls entity identity "the single most load-bearing decision in this document" — a known cheminformatics hazard (parent compound vs. salt/stereoisomer conflation) left unaddressed risks silent identity errors from the very first chemical entity ingested, which are exactly the hardest class of error to unwind later.
- **Impact:** SCHEMA.md's Entity Identity section gains an explicit caveat: chemical xrefs require a granularity check before merge, not just a namespace/ID match.
- **Risk:** Low to adopt; high to defer given Drug/Chemical entities are explicit Phase 1 scope and likely to be ingested early.
- **Dependency:** None.
- **Constitutional justification:** MASTER_CONTEXT.md Article IV; the Entity Identity section's own stated stakes.
- **Future phase:** Phase 1.

### O4 — Adopt Biolink qualifiers for directionality — **ACCEPT NOW**

- **Why:** Same category as E2 — an expressiveness gap in how every relationship is represented, not a new entity type. Bare predicates without directionality ("gene X associated with gene Y" instead of "gene X upregulates gene Y") lose information that can't be recovered later without re-deriving it from original sources.
- **Impact:** The Relationship Types section adopts Biolink's predicate-plus-qualifier pattern explicitly, rather than bare predicates, before any relationship data is ingested under the simpler pattern.
- **Risk:** Low to adopt now; meaningful information loss if real relationship data is ingested first without directionality and must be re-processed later.
- **Dependency:** None.
- **Constitutional justification:** MASTER_CONTEXT.md Article IV; Article V Rule 4 (Biolink already provides this — use the existing standard).
- **Future phase:** Phase 1.

---

## 5. Future Phase 2/3 Compatibility

### P1 — "Checked, absent" representation — **ACCEPT NOW**

- **Why:** This is a data-capture problem that can only be solved going forward from the moment ingestion begins — there is no way to retroactively know what was "checked and found nothing" for records ingested before this concept exists. VISION.md Article V Rule 5 ("absence of evidence is data") makes this foundational, not a Phase 2 nicety.
- **Impact:** SCHEMA.md defines the schema-level concept of a "checked-absent" record (what it means for an entity-pair/relationship-type combination to have been actively checked with no result). The reasoning-engine index that consumes this at scale is Phase 2's own build, not designed here.
- **Risk:** If deferred to Phase 2, all Phase 1 ingestion done in the meantime produces no "checked-absent" signal at all, permanently losing the ability to distinguish "gap" from "never looked" for that period.
- **Dependency:** None for the schema concept; the consuming index depends on Phase 2 (Biological Reasoning Engine) design.
- **Constitutional justification:** VISION.md Article V Rule 5; ROADMAP.md Article III.
- **Future phase:** Phase 1 (schema concept now); Phase 2 (index/consumption).

### P2 — `Finding` entity for Phase 2 output — **DEFER**

- **Why:** This is explicitly Phase 2's own object model, per ROADMAP.md Article III's description of Phase 2's output. Designing it now, before Phase 2 begins, risks over-specifying a structure Phase 2's actual reasoning engine design may need to shape differently — the acknowledgment already present in SCHEMA.md ("a Finding type will sit between raw graph data and research_hypothesis") is sufficient forward-reference for now.
- **Impact:** No cost to deferring — Phase 3's Hypothesis Model already anticipates a `generated_by` link to "reasoning process," leaving room for `Finding` to slot in later without restructuring the Hypothesis Model.
- **Risk:** Low. Risk would only arise if Phase 3 work started before Phase 2's `Finding` type is designed and had to guess at its shape — mitigated by the existing acknowledgment note.
- **Dependency:** Phase 2 (Biological Reasoning Engine) design.
- **Constitutional justification:** ROADMAP.md Article I ("phases overlap... Phase 2 cannot mature without Phase 1 already growing" — but Phase 2's own object model is still Phase 2's to design); MASTER_CONTEXT.md Article IV (not a license to over-build speculatively).
- **Future phase:** Phase 2.

### P3 — Active graph-staleness tracking — **DEFER**

- **Why:** The schema field this depends on (E3's provenance lifecycle status) is being accepted now; the *operational* work of actually monitoring sources for retractions and updates is a continuously-running service, which is precisely what ROADMAP.md Article VI defines Phase 5 (Autonomous Scientist) to do. Building the monitoring mechanism now, before Phase 1's ingestion even has real sources running, is premature.
- **Impact:** No cost to deferring — the schema field (E3) ensures Phase 5 has somewhere to write its findings when it arrives; deferring only the active service, not the data model.
- **Risk:** Low, contingent on E3 being adopted — without E3's field, this DEFER would instead be a Critical retrofit risk.
- **Dependency:** E3 (accepted); Phase 5 being reached.
- **Constitutional justification:** ROADMAP.md Article VI.
- **Future phase:** Phase 5.

---

## 6. Risks to the 2,000-Phase Rule

### R1 — `schema_version` tag on every record — **ACCEPT NOW**

- **Why:** This is the clearest possible instance of the exact failure mode VISION.md Article IX exists to prevent — a field that costs nothing today and becomes effectively impossible to add retroactively once billions of records exist without it. There is no version of "wait and see" that doesn't make this worse.
- **Impact:** Every node and edge in SCHEMA.md's data model gains a `schema_version` field, incremented whenever a structurally-relevant change is made to SCHEMA.md (new required fields, changed tier semantics) — tracked in a schema-level changelog, distinct from the constitutional Amendment Log.
- **Risk:** Adopting now: negligible. Deferring: high and compounding — every month of ingestion without this field is data that can never be retroactively distinguished as "valid under an earlier schema" versus "malformed."
- **Dependency:** None.
- **Constitutional justification:** VISION.md Article IX; MASTER_CONTEXT.md Article IV.
- **Future phase:** Phase 1.

### R2 — Entity split/merge lineage — **ACCEPT NOW**

- **Why:** Genes and genomes are the most central Phase 1 entity type, and genome-assembly/gene-model revisions that split or merge entities are routine in real genomics — this is not a hypothetical edge case but a near-certainty over the platform's lifetime. The Entity Identity section already handles the mirror-image problem (duplicate detection); leaving the split/merge case unaddressed is an asymmetric gap in the same load-bearing system.
- **Impact:** SCHEMA.md's Entity Identity section gains `xerdna:split_into` / `xerdna:merged_from` relationship types that preserve both old and new canonical IDs through a split or merge, rather than silently retiring or overwriting an ID.
- **Risk:** Adopting now: low, mechanical extension of an existing pattern. Deferring: high — the first real gene-model revision encountered without this mechanism would force an ad hoc, undocumented fix under time pressure, exactly the scenario Scientific Constitution Before Code exists to prevent.
- **Dependency:** None.
- **Constitutional justification:** VISION.md Article IX; the Entity Identity section's own stated stakes ("get identity wrong and every later phase inherits silent duplication or silent conflation" — split/merge is the same risk, uncovered).
- **Future phase:** Phase 1.

### R3 — New namespace-registry governance for multi-contributor scale — **REJECT**

- **Why:** The current governance (a schema-level decision requiring a recorded rationale, no Article III amendment needed) is not scale-dependent in its actual mechanics — the rationale requirement applies identically whether there is one contributor or a thousand. Designing a heavier, Phase-6-specific review process now, for a contributor scale that doesn't exist yet and whose actual failure modes are unknown, is speculative process-building disallowed by MASTER_CONTEXT.md Article IV. A governance mechanism designed against an imagined future problem risks being wrong for the real one when it arrives.
- **Impact:** No new governance mechanism is added now. The existing rationale-required registry process stands as-is.
- **Risk:** If the lightweight process genuinely proves insufficient once Phase 6 opens contribution broadly, that will surface as a concrete problem (e.g., observed namespace sprawl or conflicting extensions) rather than a hypothetical one — at which point it is addressed with evidence in hand, which produces a better-designed process than speculating now would.
- **Dependency:** None — this is a rejection of premature process design, not a rejection of the concern's eventual validity.
- **Constitutional justification:** MASTER_CONTEXT.md Article IV (not a license to over-build speculatively); Article VII Decision Principle 3 (reversibility — keeping today's lightweight process is easier to evolve from evidence than to unwind a heavier one built on guesses).
- **Future phase:** None assigned — revisit only if Phase 6 (Collective Intelligence) produces concrete evidence the current process is insufficient.

### R4 — State the Biolink abstraction boundary explicitly — **ACCEPT NOW**

- **Why:** This is a one-paragraph clarification of something SCHEMA.md's design already implies (canonical `xerdna:` IDs are the durable layer; Biolink/OBO mappings are a translation layer) — making it explicit costs nothing and removes any future ambiguity about which layer is allowed to change if Biolink itself is ever superseded.
- **Impact:** SCHEMA.md's Foundational Choice section states explicitly that XERDNA's own canonical IDs and internal type hierarchy are the durable layer; the Biolink/OBO mapping is a translation layer that could in principle be re-pointed at a successor standard without renumbering XERDNA's own entities.
- **Risk:** Negligible to adopt. This is insurance, not a response to any near-term threat — the risk it guards against (Biolink being abandoned or radically restructured) is long-horizon and low-probability, which is exactly why VISION.md Article IX asks for this kind of cheap insurance on load-bearing components.
- **Dependency:** None.
- **Constitutional justification:** VISION.md Article IX.
- **Future phase:** Phase 1.

---

## What Happens Next

This document authorizes nothing by itself. Per Scientific Constitution Before Code (VISION.md Article IX), the 15 ACCEPT NOW items become real only when applied to SCHEMA.md as explicit, individually traceable edits — a separate, subsequent step requiring its own go-ahead. The 8 DEFER items remain visible here as a standing backlog, owned by the phase noted above, so they are revisited on schedule rather than forgotten. The 2 REJECT items are closed decisions, not silence — each has a stated condition under which it would be reopened.
