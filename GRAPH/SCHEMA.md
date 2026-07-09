# GRAPH SCHEMA — Conceptual Model

**Constitutional basis:** this document implements [ROADMAP.md](../ROADMAP.md) Article II (Phase 1 — Universal Biological Memory), under [VISION.md](../VISION.md) Article IV (Evidence Principles), Article V (Scientific Principles), Article VI (AI Principles), Article VIII (Scientific Integrity as Supreme Constraint), and Article IX (permanent rules), and under [MASTER_CONTEXT.md](../MASTER_CONTEXT.md) Article II (Non-Negotiable Rules), Article IV (Long-Term Architecture Philosophy), Article V (Design Rules), and Article VI (Naming Conventions).

**Schema version:** 1.2 — see Schema Changelog, below.

It is a Level-5 document in the authority hierarchy (MASTER_CONTEXT.md Article I): it implements the constitution and must yield to it on any conflict, never the reverse. Nothing in this document is authoritative on its own — every section below cites the constitutional article it serves. This document is still conceptual architecture. It defines *what kinds of things* live in the graph, *how they connect*, *how confident the system is allowed to sound about each of them*, and *how every claim stays traceable to its source*. It does not pick a storage engine, does not ingest data, and does not constitute application code — see "What This Document Is Not."

## Foundational Choice: Build on Biolink Model + OBO Ontologies

XERDNA's vocabulary is not invented from scratch. It builds on:

- **[Biolink Model](https://biolink.github.io/biolink-model/)** — the entity/association model used by NCATS Translator and the Monarch Initiative. It defines a hierarchy of biomedical entity categories, a predicate hierarchy for relationships, and an association model with provenance and knowledge-level slots.
- **OBO Foundry ontologies** for controlled vocabulary within entities: [GO](https://geneontology.org/) (function/process/component), [ChEBI](https://www.ebi.ac.uk/chebi/) (chemicals), [Mondo](https://mondo.monarchinitiative.org/) (disease), [HPO](https://hpo.jax.org/) (phenotype), [Uberon](https://obophenotype.github.io/uberon/) (anatomy), [PRO](https://proconsortium.org/) (protein forms), [SO](http://www.sequenceontology.org/) (sequence features), [NCBITaxon](https://www.ncbi.nlm.nih.gov/taxonomy) (organisms).

**Rationale:** this is the "boring, well-understood foundation" call required by MASTER_CONTEXT.md Article IV and Article V Rule 4. Biolink and OBO already solved cross-database entity identity, predicate semantics, and hierarchical typing — problems the field spent over a decade converging on. Reinventing them would trade short-term flexibility for long-term migration risk on a component meant to carry 2,000 phases of weight (VISION.md Article IX).

### Pinned Vocabulary Versions

*Serves: GRAPH/SCHEMA_DECISIONS.md O1 (ACCEPT NOW).*

Biolink and OBO both evolve independently of this document and of each other. Every record ingested under this schema is ingested under a specific vocabulary snapshot, and that snapshot is pinned and recorded, not left implicit:

| Vocabulary | Pinned release (verified at ratification, 2026-07-09) |
|---|---|
| Biolink Model | v4.3.7 (2026-02-25) |
| GO (Gene Ontology) | releases/2026-05-19 |
| Mondo (disease) | 2026-05-18 |
| HPO (phenotype) | 2026-06-06 |
| Uberon (anatomy) | 2026-06-19 per EBI OLS; Bioregistry independently lists 2026-04-01 for the same nominal release — the discrepancy is recorded, not silently resolved, and must be rechecked before Uberon is first used in an ingestion connector |
| PRO (protein forms) | 2026_2 |
| NCBITaxon (organisms) | 2026-05-13 |
| ChEBI (chemicals) | **Not pinned.** ChEBI retired its legacy versioned release scheme in October 2025 for GitLab-tagged releases; no single canonical version identifier was independently verifiable at ratification. The first ingestion connector touching ChEBI must pin the exact release tag it uses before that connector is authorized. |
| SO (sequence features) | **Not pinned.** No independently verifiable 2026 release identifier was found at ratification. The first ingestion connector touching SO must pin the exact release it uses before that connector is authorized. |

**Upgrade policy:** an ontology version upgrade is a schema-level decision, not a constitutional amendment — the same governance already defined for the `xerdna:` Namespace Registry, below — requiring a recorded rationale for why the upgrade is being made and what, if anything, changes for already-ingested records, but not the MASTER_CONTEXT.md Article III process. Per Anti-Hallucination Rule 4 (a syntactically valid but unverified identifier is treated as absent, not as weak evidence), the two unpinned entries above are open gaps, not approximate pins — no ingestion may proceed against ChEBI or SO until each is actually pinned.

### Term-Level Verification (Biological Entity Types and Relationship Types, below)

Pinning a version (above) confirms *which release* is in effect; it does not by itself confirm every category and predicate name used later in this document is still valid under that release — Biolink has a documented history of backward-incompatible category changes across major versions. A term-by-term verification pass was performed against Biolink Model v4.3.7 specifically (via its published documentation), with these results:

- **18 of the 19 Biolink entity categories** in the Biological Entity Types table (below) were individually confirmed to exist, with definitions consistent with how this document uses them: `Genome`, `Gene`, `NucleicAcidEntity`, `Transcript`, `Protein`, `Cell`, `Pathway`, `OrganismTaxon`, `SequenceVariant`, `Drug`, `ChemicalEntity`, `ClinicalTrial`, `InformationContentEntity`, `PopulationOfIndividualOrganisms`, `Publication`, `Disease`, `PhenotypicFeature`, `AnatomicalEntity`.
- **`biolink:InformationResource` could not be confirmed as a current, standalone node category** — see the caveat directly on that row in the Biological Entity Types table, below, rather than asserting a fix here without further verification.
- **9 of the predicates** used in the Relationship Types section and its E2/O4 rules were individually confirmed: `interacts_with`, `part_of`, `gene_associated_with_condition`, `treats`, `has_phenotype`, `correlated_with`, `orthologous_to`, `expressed_in`, `causes`. Others named only as illustrative examples (e.g. `regulates`) were not individually checked.

This does not constitute a complete audit of every term Biolink defines that XERDNA might someday use — only of the terms this document currently cites. Any future addition to the Biological Entity Types or Relationship Types sections should be verified against the currently-pinned release at the time it's added, not assumed valid by analogy to terms verified here.

### The Durable Layer and the Translation Layer

*Serves: GRAPH/SCHEMA_DECISIONS.md R4 (ACCEPT NOW).*

XERDNA's own canonical IDs (the `xerdna:` namespace, see Entity Identity below) and internal type hierarchy are the durable layer of this schema — the part meant to survive 2,000 phases regardless of what happens to any external standard (VISION.md Article IX). The Biolink/OBO mapping above is a translation layer: it lets XERDNA speak a vocabulary the field already uses, but XERDNA's own identity does not depend on it. If Biolink or an OBO ontology is ever abandoned, forked, or restructured beyond what the Upgrade Policy above can absorb, the translation layer is what gets re-pointed at a successor standard — XERDNA's own canonical IDs are never renumbered to follow it.

### Precedence when Biolink conflicts with the constitution

Biolink is the vocabulary base, not a governing authority — MASTER_CONTEXT.md Article I places this document, and everything it adopts from Biolink, below the constitution. Two concrete places where XERDNA is stricter than Biolink's defaults:

1. **Biolink's `knowledge_level` and provenance slots are optional; XERDNA's are not.** Biolink permits an association to omit `knowledge_level` or `primary_knowledge_source` (`not_provided` is a valid value). XERDNA's Evidence Model (below) makes `evidence_tier` and `primary_knowledge_source` mandatory on every node and edge, per MASTER_CONTEXT.md Article II Rule 1 — a Biolink-valid record that omits them is not XERDNA-valid and is rejected.
2. **Biolink has no native concept of a research hypothesis with contradicting evidence and reasoning.** Its `knowledge_level` enum (`knowledge_assertion`, `logical_entailment`, `prediction`, `observation`, `statistical_association`, `not_provided`) has nothing resembling VISION.md Article IV's third tier. XERDNA extends Biolink's association model with a `research_hypothesis` value and the additional fields the Hypothesis Model (below) requires, rather than overloading `prediction` to mean two different things.

Wherever a future ingestion source's native Biolink representation is looser than the constitution allows, the constitution wins and the data is either upgraded with the missing fields at ingestion or rejected — never imported as-is with a gap.

XERDNA extends the Biolink/OBO base rather than replacing it: anything it doesn't cover (e.g. patents) gets a namespaced `xerdna:` extension class that subtypes the nearest Biolink category, never an untyped ad hoc node (MASTER_CONTEXT.md Article V Rule 3).

## Biological Entity Types

*Serves: ROADMAP.md Article II (Phase 1 entity list); MASTER_CONTEXT.md Article V Rule 1 (typed, never ad hoc).*

Each row maps a Roadmap Phase 1 entity to its Biolink (or OBO, or XERDNA-extension) type.

| Roadmap entity | Type | Source |
|---|---|---|
| Genome | `biolink:Genome` | Biolink |
| Gene | `biolink:Gene` | Biolink |
| DNA / RNA (sequence features, transcripts) | `biolink:NucleicAcidEntity`, `biolink:Transcript` | Biolink |
| Protein | `biolink:Protein` | Biolink |
| Protein structure | `xerdna:ProteinStructure` (subtype of `biolink:Protein`; carries a structure-source field — experimental (PDB) vs. predicted (e.g. AlphaFold). The evidence tier, not the type, is what disambiguates fact from prediction) | XERDNA extension |
| Cell type | `biolink:Cell` | Biolink |
| Pathway | `biolink:Pathway` | Biolink |
| Organism / taxon (for evolution) | `biolink:OrganismTaxon` | Biolink / NCBITaxon |
| Mutation / variant | `biolink:SequenceVariant` | Biolink |
| Drug / chemical | `biolink:Drug`, `biolink:ChemicalEntity` | Biolink / ChEBI |
| Clinical trial | `biolink:ClinicalTrial` | Biolink |
| Patent | `xerdna:Patent` (subtype of `biolink:InformationContentEntity`) | XERDNA extension — not in core Biolink |
| Microbiome | `xerdna:MicrobialCommunity` (subtype of `biolink:PopulationOfIndividualOrganisms`) | XERDNA extension |
| Scientific literature | `biolink:Publication` | Biolink |
| Public database / source | **Not confirmed as a standalone Biolink node category under v4.3.7** — see Term-Level Verification, above. Biolink's current, verified mechanism for representing a knowledge source is the `infores:` CURIE identifier used as the *value* of the `primary_knowledge_source` / `aggregator_knowledge_source` slots (Provenance Model, below) — not necessarily a node typed in its own right. Until re-verified or amended, a "Public database / source" reference should be carried via those slots rather than minted as a `biolink:InformationResource`-typed node. | Open — flagged, not silently corrected (Anti-Hallucination Rule 4) |

Disease, phenotype, and anatomy categories (`biolink:Disease`, `biolink:PhenotypicFeature`, `biolink:AnatomicalEntity`) aren't named explicitly in the Roadmap's Phase 1 list but are load-bearing connective tissue for genes/mutations/drugs — included now rather than retrofitted later (MASTER_CONTEXT.md Article IV).

## Relationship Types

*Serves: ROADMAP.md Article II; MASTER_CONTEXT.md Article V Rule 1.*

Relationships use Biolink's predicate hierarchy (e.g. `biolink:interacts_with`, `biolink:part_of`, `biolink:gene_associated_with_condition`, `biolink:treats`, `biolink:has_phenotype`, `biolink:correlated_with`, `biolink:orthologous_to`, `biolink:expressed_in`). New predicates are added under an `xerdna:` namespace only when no Biolink predicate fits (patents referencing genes/drugs are the most likely early case: `xerdna:claims`, `xerdna:cites`).

A relationship is never a bare edge — it is always an **association**, carrying every field defined in the Evidence, Provenance, Confidence, Hypothesis, and Prediction Models below. This is what makes the graph queryable by confidence and traceable to source, not just traversable.

**Rule — correlation defaults, causation is earned** (GRAPH/SCHEMA_DECISIONS.md E2, ACCEPT NOW): a relationship extracted or ingested from a statistical-association finding (e.g. a GWAS hit) defaults to a correlational predicate (`biolink:correlated_with` or an equivalent weaker predicate) and is never upgraded to a causal predicate (e.g. `biolink:causes`) unless the source itself asserts and supports causation. Strength of statistical association is not evidence of causation, and defaulting to the weaker predicate is what keeps this distinction from being blurred at ingestion (VISION.md Article VIII).

**Rule — predicate plus qualifier, not bare predicates** (GRAPH/SCHEMA_DECISIONS.md O4, ACCEPT NOW): wherever Biolink defines a qualifier for a relationship (e.g. an object-direction qualifier distinguishing "upregulates" from "downregulates" under a shared `regulates` predicate), the qualifier is captured alongside the predicate, not discarded. A bare predicate is used only when no qualifier applies or none is yet known from the source — never as a substitute for a qualifier the source actually supports.

## Evidence Model

*Serves: VISION.md Article IV (Evidence Principles); MASTER_CONTEXT.md Article II Rule 1.*

Every node and every edge carries exactly one `evidence_tier`:

| Tier | Meaning | Who/what may assign it |
|---|---|---|
| `established_evidence` | Peer-reviewed, reproduced, or otherwise scientifically validated fact | Only structured ingestion from a recognized authoritative source (a named database, a peer-reviewed publication record) — never assigned by free-text generation or inference (see Anti-Hallucination Rules) |
| `computational_prediction` | Output of a model, simulation, or algorithm — not yet validated | Any named, versioned model or pipeline (human or AI) |
| `research_hypothesis` | A generated, evidence-ranked question worth investigating | XERDNA's reasoning/hypothesis engine (Phase 2/3), or a contributing researcher (Phase 6) |

**Rule:** a record with no `evidence_tier` does not enter the graph. This is a data-quality gate enforced at the boundary, not a display label applied afterward (VISION.md Article IV).

**Structural consequence:** because the three tiers must stay distinguishable at every surface (VISION.md Article VIII), they are not just different values of one field — they carry different *required* field sets, defined in the Provenance, Confidence, Hypothesis, and Prediction Models below. A `research_hypothesis` record missing `contradicting_evidence` is as invalid as an `established_evidence` record missing a publication reference.

**Rule — every source needs its own tiering rubric** (GRAPH/SCHEMA_DECISIONS.md E1, ACCEPT NOW): "recognized authoritative source" in the table above is not self-evident and is not decided ad hoc per record. Every source-specific design document (in `DATA/`) must state, before its ingestion connector is authorized, an explicit rubric for which of that source's records qualify for `established_evidence` versus `computational_prediction` — e.g., distinguishing a database's manually curated, peer-reviewed records from its automatically annotated ones, where both exist within the same source. A source design document without this rubric does not authorize an ingestion connector.

**Rule — conflicting established evidence is preserved, not resolved at ingestion** (GRAPH/SCHEMA_DECISIONS.md E4, ACCEPT NOW): two contradictory `established_evidence` edges between the same nodes (e.g. two peer-reviewed sources disagreeing) are an expected, valid graph state — not a data-quality error to fix by dropping one side. Ingestion never "resolves" a conflict between two otherwise-valid `established_evidence` records; both are kept, both traceable to their own source. Reconciling or explaining the conflict is the Biological Reasoning Engine's job (ROADMAP.md Article III), not ingestion's.

## Provenance Model

*Serves: VISION.md Article V Rule 4 (reproducibility); MASTER_CONTEXT.md Article V Rule 2 (provenance mandatory).*

Every node and edge, regardless of tier, carries:

| Field | Meaning |
|---|---|
| `primary_knowledge_source` | The originating database, tool, or model (e.g. `infores:uniprot`, `infores:alphafold`) — the immediate origin of this record |
| `aggregator_knowledge_source` | Any intermediate system that passed the record through before XERDNA ingested it (e.g. a federated API aggregator) — recorded so a broken or biased aggregator can be identified and audited later, not just the original source |
| `retrieved_at` | Timestamp of ingestion into XERDNA — provenance is a point-in-time claim; upstream sources get corrected or retracted, and XERDNA must know which version of the world it ingested |
| `source_record_id` | The exact identifier of the record at the source (accession number, DOI, model run ID) — enables re-fetching the original to verify a claim, not just trusting the copy in the graph |
| `status` | `active` \| `retracted` \| `superseded_by:<id>` — defaults to `active` at ingestion; records whether the source has since been retracted, corrected, or superseded, independent of when the record was first retrieved |

**Rule:** a record missing `primary_knowledge_source` or `source_record_id` does not enter the graph — there is no such thing as an anonymous fact in XERDNA (MASTER_CONTEXT.md Article V Rule 2).

**Rule — `status` defaults to active, not to permanence** (GRAPH/SCHEMA_DECISIONS.md E3, ACCEPT NOW): `status` exists so a later retraction or supersession has somewhere to be recorded without touching `retrieved_at` (a point-in-time claim) or rewriting history. No active monitoring service is implied by this field at Phase 1 — the field is the prerequisite for Phase 5's Autonomous Scientist (ROADMAP.md Article VI) to later attach that monitoring, not the monitoring itself.

## Schema Versioning

*Serves: VISION.md Article IX ("Build for 2,000 phases"); GRAPH/SCHEMA_DECISIONS.md R1 (ACCEPT NOW).*

Every node and edge, regardless of tier, additionally carries a `schema_version` field: the version of this document (see Schema Changelog, below) in effect when the record was created. `schema_version` is incremented whenever a structurally-relevant change is made to this document — a new required field, a changed tier semantic, a new universal rule — not for wording or clarification edits.

**Rule:** `schema_version` is what lets a future reader distinguish "an old record, valid under an earlier version of this schema" from "a malformed record" once a new required field exists that older records don't have. Without it, the two are indistinguishable at scale.

### Schema Changelog

Distinct from the constitutional Amendment Log (MASTER_CONTEXT.md Article XI) — this changelog tracks changes to this document only.

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-07-09 | Initial conceptual model, ratified — see the Constitutional basis line at the top of this document for what it traces to. |
| 1.1 | 2026-07-09 | Applied all 15 ACCEPT NOW items from [GRAPH/SCHEMA_DECISIONS.md](SCHEMA_DECISIONS.md): pinned vocabulary versions and stated the durable/translation layer boundary (O1, R4); correlation-defaults and predicate-qualifier rules (E2, O4); ingestion-time tiering rubric requirement and conflicting-evidence-is-valid rule (E1, E4); provenance `status` field (E3); hypothesis subgraph-scoped claims, promotion boundary, and non-terminal status (H2, H1, H4); prediction `method` controlled-vocabulary binding (O2); chemical-identity granularity check and split/merge lineage (O3, R2); checked-absent records (P1); this `schema_version` field and changelog (R1). |
| 1.2 | 2026-07-09 | Closed the four blockers from [DOCS/PHASE_001_APPROVAL_V2.md](../DOCS/PHASE_001_APPROVAL_V2.md): performed a term-level verification pass of the Biological Entity Types and Relationship Types sections against pinned Biolink v4.3.7, confirming 18/19 entity categories and 9 cited predicates, and flagging `biolink:InformationResource` as unconfirmed rather than silently correcting it (B2); reconciled Checked-Absent Records against Article II Rule 1 and the association requirement, stating its exemption explicitly (B3); extended the Namespace Registry's governance scope to explicitly cover `xerdna:` predicates, not only entity-type prefixes (B4). (B1, the Article X/Article I ordering clarification, was applied to MASTER_CONTEXT.md directly and does not touch this document.) |

## Confidence Model

*Serves: VISION.md Article VIII (tiers must not blur); MASTER_CONTEXT.md Article II Rule 1.*

Confidence is not a single universal field — its meaning and even its presence depends on the tier, because collapsing them into one numeric field is exactly the kind of blurring VISION.md Article VIII forbids:

- **`established_evidence` carries no `confidence` field at all.** Established evidence is binary in this model — either a claim is backed by a citable, validated source, or it is not established evidence. Attaching a confidence number to it would imply established facts come in degrees of trust, undermining the tier's entire purpose.
- **`computational_prediction` carries a `confidence` field** — numeric where the producing method natively outputs one (e.g. a model probability), qualitative (`low`/`medium`/`high`) where it doesn't. It must state which kind it is (`confidence_type: numeric | qualitative`), so a numeric-looking score from a non-probabilistic model is never mistaken for a calibrated probability.
- **`research_hypothesis` carries a `confidence` field** describing how strongly the supporting evidence outweighs the contradicting evidence — always qualitative at this phase (XERDNA does not yet claim the ability to calibrate hypothesis confidence numerically; claiming false precision here would itself violate VISION.md Article VIII).

**Rule:** an uncalibrated confidence score is never displayed or queried as if it were a probability of truth. `confidence_type` exists specifically so downstream consumers (Phase 2 onward) can't accidentally treat "0.8 similarity score" as "80% likely true."

## Hypothesis Model

*Serves: ROADMAP.md Article IV (Phase 3 — Hypothesis Engine); VISION.md Article V Rule 3 (refutation is signal).*

A `research_hypothesis`-tier record is a structured object, not a sentence with a tag. It requires:

| Field | Meaning |
|---|---|
| `claim` | The hypothesis statement itself, scoped to a specific set of graph entities and edges — a single relationship or an arbitrary subgraph (e.g. a mechanism spanning three or more entities) — never free text disconnected from the graph |
| `supporting_evidence` | References to graph nodes/edges (or external publications) that support the claim |
| `contradicting_evidence` | References to graph nodes/edges (or external publications) that weigh against the claim — required even if empty-and-explicit (`none_found_as_of: <date>`), so absence of contradiction is a recorded state, not a silent omission |
| `confidence` | Per the Confidence Model above |
| `reasoning` | An explanation of how the hypothesis was derived from the supporting/contradicting evidence — a hypothesis without this is not admissible (VISION.md Article VI Rule 4) |
| `status` | `open` \| `under_investigation` \| `refuted` \| `supported_by_experiment` — set only by human/experimental input, never by the system itself (VISION.md Article VI Rule 5); the system may propose a status change, never assert one |
| `generated_by` | Which reasoning process or contributor produced it (Phase 3 engine, a named researcher in Phase 6, etc.) |

**Rule:** `status` transitions into `refuted` or `supported_by_experiment` are themselves evidence-tier `established_evidence` events (an experiment's finding is established evidence about the hypothesis) — this is how the graph stays a closed loop between hypotheses and the evidence that eventually resolves them (ROADMAP.md Article VII).

**Rule — a prediction is never promoted to a hypothesis by confidence alone** (GRAPH/SCHEMA_DECISIONS.md H1, ACCEPT NOW): a `computational_prediction` may be cited by a `research_hypothesis` as `supporting_evidence`, but no prediction becomes a hypothesis merely by crossing a confidence threshold. Promotion requires an explicit reasoning step (the Phase 2/3 reasoning or hypothesis engine, or a contributing researcher in Phase 6) that produces the `claim`, `contradicting_evidence`, and `reasoning` fields this model requires — a high-confidence prediction with no such step remains a prediction.

**Rule — no `status` value is permanently terminal** (GRAPH/SCHEMA_DECISIONS.md H4, ACCEPT NOW): `refuted` and `supported_by_experiment` are not end states. Per VISION.md Article III, XERDNA is not "done" at any point, and new `established_evidence` may reopen a hypothesis previously marked either way — the same human/experimental-input requirement above governs any such transition, in either direction.

## Prediction Model

*Serves: ROADMAP.md Article II, Article V (Simulator); VISION.md Article VI Rule 3 (method transparency).*

A `computational_prediction`-tier record requires:

| Field | Meaning |
|---|---|
| `method` | The named algorithm, model, or pipeline that produced it, bound to a controlled-vocabulary term (e.g. OBI — Ontology for Biomedical Investigations) where one exists for that method or assay type |
| `model_version` | The specific version — a prediction from an unversioned or unnamed method is not reproducible and is rejected (VISION.md Article VI Rule 3) |
| `input_reference` | What graph data or external input the model was run on — a prediction with no recorded input can't be reproduced or audited |
| `confidence` | Per the Confidence Model above |
| `generated_at` | When the model was run — distinct from `retrieved_at` in the Provenance Model, since a prediction can be generated long after (or before) it's ingested |

**Rule:** predictions are never silently promoted to `established_evidence` when they turn out to be right — a promotion requires an independent `established_evidence` record (e.g. a citation of the experiment that confirmed it), linked to, not substituted for, the original prediction. The prediction's history is preserved either way (VISION.md Article V Rule 3 — refutation and confirmation are both signal, not reasons to erase history).

**Rule — `method` binds to a controlled vocabulary, or flags the gap** (GRAPH/SCHEMA_DECISIONS.md O2, ACCEPT NOW): `method` is never indefinite free text. Where a controlled-vocabulary term exists for the method or assay type, it is used. Where none exists yet, the record states `ontology_gap: true` alongside the free-text method name, making the gap visible and auditable rather than letting untyped method names accumulate silently. The specific controlled vocabulary to bind against is chosen deliberately, the same way Biolink/OBO were chosen (Foundational Choice, above), once a real prediction-generating pipeline exists to bind against.

## Checked-Absent Records

*Serves: VISION.md Article V Rule 5 (absence of evidence is data); ROADMAP.md Article III (Phase 2 — research gaps); GRAPH/SCHEMA_DECISIONS.md P1 (ACCEPT NOW).*

Not every entity-pair/relationship-type combination XERDNA has looked at has a result — and the schema must be able to say so, distinct from simply never having asked. A `checked_absent` record states that a specific relationship type between a specific pair (or set) of entities was actively checked, by a named `method` (per the Prediction Model) or a named ingestion pass over a source, and no supporting record was found as of a given date.

| Field | Meaning |
|---|---|
| `subject`, `predicate`, `object` | The relationship type and entities that were checked |
| `checked_by` | The method, pipeline, or ingestion pass that performed the check |
| `checked_at` | When the check was performed |
| `scope` | What was actually checked (e.g. "PubMed abstracts indexed as of `checked_at`") — a checked-absent record is only as strong as what it claims to have covered |

**Rule:** a `checked_absent` record is not itself evidence that no relationship exists — it is evidence that XERDNA looked and found nothing within its stated `scope`. The reasoning engine (Phase 2) is what turns a density of `checked_absent` records into a surfaced research gap; this schema only defines what a single check-and-found-nothing event looks like, so that signal exists from Phase 1 forward instead of being unrecoverable for data ingested before Phase 2 begins.

**Rule — `checked_absent` is exempt from the tier and association requirements, explicitly:** MASTER_CONTEXT.md Article II Rule 1 requires every "biological claim" entering the graph to carry one of the three evidence tiers, and the Relationship Types section above requires every relationship to be a tiered "association." A `checked_absent` record asserts neither — it is not a claim about biology (it makes no statement that a relationship does or doesn't exist in reality) and it is not an association (it carries no `evidence_tier`, `confidence`, or Hypothesis/Prediction Model fields). It is a third, narrower category: a process record documenting that XERDNA's own search activity occurred, scoped and timestamped. This exemption is stated here explicitly, rather than left as an inference, per this schema's own standard of not leaving required-versus-exempt status implicit (Anti-Hallucination Rules, below).

## Entity Identity & Cross-Referencing

*Serves: MASTER_CONTEXT.md Article VI Rule 4 (namespaced identity).*

Every canonical node has:

- **A canonical XERDNA ID**, namespaced by type: `xerdna:gene:<id>`, `xerdna:protein:<id>`, etc. — internal, stable, never reused even if the entity is later deprecated.
- **A set of external xrefs** — the same biological entity is named differently by every source database (a gene has an HGNC symbol, an NCBI Gene ID, an Ensembl ID, a UniProt accession for its protein product). Xrefs are a list of `(namespace, id)` pairs, e.g. `[("HGNC", "1100"), ("NCBIGene", "672"), ("Ensembl", "ENSG00000012048")]`.
- **An identity resolution policy**: when ingestion encounters an entity already present under a different source ID, it resolves to the existing canonical node and appends the xref — it does not create a duplicate. Unresolvable ambiguity (two sources disagreeing on whether two records are the same entity) is itself recorded as a `research_hypothesis`-tier relationship (`xerdna:possibly_same_as`) rather than silently merged or silently dropped.

**Rule — chemical identity requires a granularity check** (GRAPH/SCHEMA_DECISIONS.md O3, ACCEPT NOW): chemical xrefs (ChEBI, PubChem CID, InChIKey, DrugBank ID) frequently name different structural granularities of "the same" compound — a parent compound versus a specific salt or stereoisomer. Entity resolution for chemicals never merges on a shared xref alone; it first checks that the xrefs agree at the same granularity. Where they don't, the mismatch is recorded, not silently merged (the same discipline as the unresolvable-ambiguity case above).

**Rule — split and merge are tracked, not just duplicates** (GRAPH/SCHEMA_DECISIONS.md R2, ACCEPT NOW): the identity resolution policy above handles two source records turning out to be one real entity. The reverse and more disruptive case — one canonical entity later found to be two distinct entities (e.g. a gene model revision), or two canonical entities later found to be one — is tracked with `xerdna:split_into` / `xerdna:merged_from` relationships that preserve both the old and new canonical IDs. A split or merge never silently retires or overwrites a canonical ID; the lineage stays queryable, not just corrected.

This is the single most load-bearing identity decision in this document: get it wrong and every later phase inherits silent duplication or silent conflation.

## The `xerdna:` Namespace Registry (Conceptual Design)

*Serves: MASTER_CONTEXT.md Article VI Rule 4.*

The identity model depends on `xerdna:` being a controlled namespace, not a free-form prefix anyone can extend informally. This section defines the *shape* of that control, not its storage mechanism (deferred, per "What This Document Is Not").

A namespace registry entry defines:

| Field | Meaning |
|---|---|
| `prefix` | The type segment after `xerdna:`, e.g. `gene`, `protein`, `Patent`, `MicrobialCommunity` |
| `parent_type` | The Biolink or OBO category it subtypes (empty only for core Biolink types used directly) |
| `introduced_in` | Which design document first defined it |
| `rationale` | Why an existing Biolink/OBO type didn't already cover it — required for every entry |
| `status` | `active` \| `deprecated` — a deprecated prefix is never reused for a different meaning |

**Governance:** adding a new `xerdna:` prefix is a schema-level decision, not a constitutional amendment — it doesn't require the MASTER_CONTEXT.md Article III process, but does require a recorded `rationale` so a future maintainer can audit why the base vocabulary wasn't sufficient.

**Scope — this registry governs `xerdna:` predicates as well as `xerdna:` entity-type prefixes.** The field schema above (`prefix`, `parent_type`, `introduced_in`, `rationale`, `status`) applies identically to a relationship predicate minted under the `xerdna:` namespace (e.g. `xerdna:claims`, `xerdna:cites`, `xerdna:possibly_same_as`, `xerdna:split_into`, `xerdna:merged_from` — all defined elsewhere in this document) as to an entity-type prefix; for a predicate, `parent_type` names the nearest Biolink predicate it would subtype or sit alongside, or is left empty with its `rationale` stating that no Biolink predicate covers the relationship at all. Every `xerdna:` predicate named in this document is retroactively subject to this registry the same as every `xerdna:` entity type — this clause closes what was previously an unstated gap, not a new mechanism.

## Extensibility Rule

*Serves: MASTER_CONTEXT.md Article V Rule 3.*

New entity or predicate types are added by:
1. Checking if a Biolink or OBO type already fits — use it.
2. If not, defining an `xerdna:` extension class that subtypes the nearest existing Biolink category.
3. Never introducing an untyped or "misc" node/edge.

## Anti-Hallucination Rules

*Serves: VISION.md Article VI (AI Principles); Article VIII (Scientific Integrity as Supreme Constraint).*

These bind every future AI component that reads, writes, or reasons over the graph (extraction pipelines, the reasoning engine, the hypothesis engine, the simulator):

1. **No entity without a resolvable origin.** A node may only be created if it has either a resolvable external xref (Entity Identity section) or an explicit, logged rationale for minting a new canonical ID with none. An AI extraction process may never invent an entity that doesn't trace to a real source record.
2. **No relationship without a source span.** Any relationship extracted from literature or free text must retain a pointer to the exact source passage it was extracted from — not a paraphrase, not a summary. If the source span can't be located, the relationship is not ingested.
3. **`established_evidence` is never assigned by generative inference.** Only direct, structured ingestion from a recognized authoritative source may set `evidence_tier: established_evidence`. An LLM or reasoning component may propose that something looks well-established, but its own output is `computational_prediction` or `research_hypothesis` at most, per VISION.md Article VI Rule 2 (no autonomous claims).
4. **Citations must resolve, not merely look plausible.** A DOI, PMID, or accession number is verified to resolve to a real record before being attached as `supporting_evidence` or a `publications` reference. A syntactically valid but unverified identifier is treated as absent, not as weak evidence.
5. **No silent fuzzy merging of identity.** Entity resolution (Entity Identity section) never merges two records based on similarity-score judgment alone, however confident the model is. Below a defined certainty threshold, the system records `xerdna:possibly_same_as` as a hypothesis, never a merge.
6. **Confidence is never invented to fill a required field.** If a method doesn't natively produce a confidence value, the record states `confidence_type: qualitative` with an explicit qualitative judgment and its basis — it does not synthesize a numeric score to satisfy the schema.
7. **Reasoning must be inspectable, not post-hoc rationalization.** The `reasoning` field in the Hypothesis Model must reflect the actual evidence graph traversal or method that produced the hypothesis — an AI component may not generate a plausible-sounding explanation disconnected from how the hypothesis was actually derived.
8. **Every generated record is re-derivable.** Given the same inputs and the same `method`/`model_version`, it must be possible to trace a prediction or hypothesis back through its inputs — an opaque, non-reproducible output does not enter the graph (VISION.md Article V Rule 4).

## Scientific Integrity Constraints

*Serves: VISION.md Article VIII (Scientific Integrity as Supreme Constraint); Article VII (Ethical Principles).*

1. **The tier is structural, not cosmetic.** `evidence_tier` is not a label added to a generic record — the required field set differs by tier (Evidence, Confidence, Hypothesis, Prediction Models above), so it is structurally impossible to construct a fully-populated record without also deciding which tier it is.
2. **No query or view may drop the tier.** Any future API, UI, or export path that can return graph data without also surfacing its `evidence_tier` and `primary_knowledge_source` is a constitutional violation (VISION.md Article IV), not a missing feature to add later.
3. **No aggregate operation may launder tiers.** A future reasoning or summarization step that combines multiple records into a new claim must propagate the weakest tier among its inputs (a summary built partly from a hypothesis is itself no stronger than a hypothesis) — it can never round up to a stronger tier than its evidence supports.
4. **Ethical constraints are pre-conditions, not post-hoc filters.** Biosecurity, privacy, and attribution rules (VISION.md Article VII) apply at ingestion and generation time, not as a moderation pass applied after content already exists in the graph.

## What This Document Is Not

- **Not a storage engine choice.** Property graph (e.g. Neo4j) vs. RDF triple store vs. hybrid is a separate, deferred decision for `DATA/` (ingestion) design — this model is expressible in either.
- **Not a complete Phase 1 backlog.** Per-source ingestion connectors (UniProt, ClinicalTrials.gov, PubMed, DrugBank, PDB, etc.) get their own design docs in `DATA/` as they're built.
- **Not implementation.** No database, API, or application code is authorized by this document — per Scientific Constitution Before Code (VISION.md Article IX), that requires an explicit, separate go-ahead.
- **Not final.** This is a first pass meant to be pressure-tested against a real ingestion source before being treated as settled — see Open Questions.

## Open Questions / Next Steps

- Pick the graph storage backend (informed by, not blocking, this model).
- Stand up the `xerdna:` namespace registry as a concrete artifact (even a flat file) before the first ingestion connector is written. This is implementation and awaits explicit go-ahead.
- Pick one real source (e.g. UniProt or HGNC) to run an end-to-end ingestion-to-node test against this schema, to validate it before it's load-bearing for more sources. This crosses into `DATA/` and is also implementation — same caveat.
