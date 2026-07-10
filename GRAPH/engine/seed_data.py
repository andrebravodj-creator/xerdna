"""
The Section 7 seed dataset -- pure declarative data, no gate calls.

Traces to: DOCS/PHASE_002_DESIGN.md Section 7 (Seed Data). "Illustrative,
Not Ingestion" per that section's own title -- these are hand-authored
fixtures, not sourced from any real external connector (Section 2's
explicit-out-of-scope list: real ingestion connectors are DATA/'s future
work).

This module defines *what* the dataset is. GRAPH/engine/ingest.py defines
*how* it is loaded -- exclusively through GRAPH/engine/gate.py's public
functions. No SQL of any kind appears in this file.

Every dict below matches the keyword-argument names of the gate.py
function it will eventually be passed to (see ingest.py), so the mapping
from fixture to gate call is direct and auditable, not implicit.
"""

SCHEMA_VERSION = "1.2"  # matches GRAPH.engine.config.SUPPORTED_SCHEMA_VERSION; not imported to keep this module data-only

# --- Namespace registry prerequisite (B4) ---
# xerdna:split_into must be registered before ENTITY_LINEAGE (below) can be
# inserted -- this row itself is inserted via a raw namespace-registry
# helper in ingest.py, since GRAPH/SCHEMA.md's Namespace Registry has no
# dedicated gate.py insert function (it is Level-5 governance data, not a
# biological record) -- see ingest.py's own note on this one exception.
NAMESPACE_REGISTRY_ENTRIES = [
    {
        "prefix": "split_into",
        "kind": "predicate",
        "parent_type": None,
        "introduced_in": "DOCS/PHASE_002_DESIGN.md",
        "rationale": "R2 split/merge lineage -- GRAPH/SCHEMA.md Entity Identity section",
    },
]

# --- Nodes (Section 7: "3 entity categories... enough to form a
# subgraph-scoped hypothesis spanning three or more entities") ---
# Two Protein instances are used, not one, because Section 7's
# `interacts_with` predicate is protein-protein -- a real interaction
# needs two distinct proteins, not a self-loop.
NODES = [
    {
        "xerdna_id": "xerdna:gene:001",
        "category": "biolink:Gene",
        "evidence_tier": "established_evidence",
        "primary_knowledge_source": "infores:hgnc",
        "source_record_id": "HGNC:1100",
        "retrieved_at": "2026-07-10",
        "xrefs": [("HGNC", "1100"), ("NCBIGene", "672")],
    },
    {
        "xerdna_id": "xerdna:protein:001",
        "category": "biolink:Protein",
        "evidence_tier": "established_evidence",
        "primary_knowledge_source": "infores:uniprot",
        "source_record_id": "P38398",
        "retrieved_at": "2026-07-10",
        "xrefs": [("UniProt", "P38398")],
    },
    {
        "xerdna_id": "xerdna:protein:002",
        "category": "biolink:Protein",
        "evidence_tier": "established_evidence",
        "primary_knowledge_source": "infores:uniprot",
        "source_record_id": "P51587",
        "retrieved_at": "2026-07-10",
        "xrefs": [("UniProt", "P51587")],
    },
    {
        "xerdna_id": "xerdna:disease:001",
        "category": "biolink:Disease",
        "evidence_tier": "established_evidence",
        "primary_knowledge_source": "infores:hgnc",
        "source_record_id": "MONDO:0007254",
        "retrieved_at": "2026-07-10",
        "xrefs": [("MONDO", "0007254")],
    },
]

# --- Valid associations (Section 7: interacts_with, correlated_with) ---
VALID_ASSOCIATIONS = [
    {
        "fixture_id": "interacts_with",
        "subject_id": "xerdna:protein:001",
        "object_id": "xerdna:protein:002",
        "predicate": "biolink:interacts_with",
        "evidence_tier": "established_evidence",
        "primary_knowledge_source": "infores:uniprot",
        "source_record_id": "STUDY:INTERACT:1",
        "retrieved_at": "2026-07-10",
    },
    {
        "fixture_id": "correlated_with",
        "subject_id": "xerdna:gene:001",
        "object_id": "xerdna:disease:001",
        "predicate": "biolink:correlated_with",
        "evidence_tier": "established_evidence",
        "primary_knowledge_source": "infores:hgnc",
        "source_record_id": "STUDY:CORR:1",
        "retrieved_at": "2026-07-10",
    },
]

# --- Computational prediction, later promoted (Section 7, Section 5.3) ---
PREDICTION = {
    "subject_id": "xerdna:gene:001",
    "object_id": "xerdna:disease:001",
    "predicate": "biolink:correlated_with",
    "evidence_tier": "computational_prediction",
    "primary_knowledge_source": "infores:xerdna-model",
    "source_record_id": "RUN:PRED:1",
    "retrieved_at": "2026-07-10",
    "prediction_method": "gradient-boosted-association-model",
    "prediction_model_version": "0.1.0",
    "prediction_input_reference": "xerdna:gene:001, xerdna:disease:001",
    "prediction_generated_at": "2026-07-10",
    "confidence_type": "numeric",
    "confidence_value": "0.81",
}

PREDICTION_PROMOTION = {
    "subject_id": "xerdna:gene:001",
    "object_id": "xerdna:disease:001",
    "predicate": "biolink:correlated_with",
    "primary_knowledge_source": "infores:hgnc",
    "source_record_id": "STUDY:CONFIRM:1",
    "retrieved_at": "2026-07-11",
}

# --- Research hypothesis, later resolved (Section 7, H2, Section 5.3) ---
HYPOTHESIS = {
    "subject_id": "xerdna:gene:001",
    "object_id": "xerdna:disease:001",
    "predicate": "biolink:gene_associated_with_condition",
    "primary_knowledge_source": "infores:xerdna-reasoning",
    "source_record_id": "HYP:1",
    "retrieved_at": "2026-07-10",
    "claim": "Gene xerdna:gene:001, via its product Protein xerdna:protein:001's interaction with "
             "xerdna:protein:002, may modulate Disease xerdna:disease:001",
    "supporting_evidence": "xerdna:gene:001 correlated_with xerdna:disease:001; "
                            "xerdna:protein:001 interacts_with xerdna:protein:002",
    "reasoning": "Co-occurrence of the gene-disease correlation and a known interaction between the "
                 "gene's protein product and a second protein suggests a plausible mechanistic path "
                 "worth investigating, though no direct causal evidence exists yet.",
    "generated_by": "xerdna-milestone-003-hand-authored-seed",
    "confidence_basis": "two independent structural signals (correlation + interaction) point the same direction",
    "none_found_as_of": "2026-07-10",
}

HYPOTHESIS_RESOLUTION = {
    "new_status": "supported_by_experiment",
    "subject_id": "xerdna:gene:001",
    "object_id": "xerdna:disease:001",
    "predicate": "biolink:gene_associated_with_condition",
    "primary_knowledge_source": "infores:hgnc",
    "source_record_id": "EXPERIMENT:1",
    "retrieved_at": "2026-07-12",
}

# --- Checked-absent record (Section 7, P1) ---
CHECKED_ABSENT = {
    "subject": "xerdna:protein:001",
    "predicate": "biolink:correlated_with",
    "object": "xerdna:disease:001",
    "checked_by": "manual seed, Milestone 003",
    "checked_at": "2026-07-10",
    "scope": "hand-authored seed only -- not a real literature or database check",
}

# --- Entity split (Section 7, R2, T15) ---
ENTITY_SPLIT_NEW_NODE = {
    "xerdna_id": "xerdna:gene:001-b",
    "category": "biolink:Gene",
    "evidence_tier": "established_evidence",
    "primary_knowledge_source": "infores:hgnc",
    "source_record_id": "HGNC:1100-rev2",
    "retrieved_at": "2026-07-13",
    "xrefs": [("HGNC", "1100")],
}

ENTITY_LINEAGE = {
    "old_xerdna_id": "xerdna:gene:001",
    "new_xerdna_id": "xerdna:gene:001-b",
    "relation": "split_into",
    "recorded_at": "2026-07-13",
}

# --- Deliberately invalid fixtures, proving rejection + atomic rollback ---
# INVALID_CAUSES is the exact case Section 7 itself specifies as an
# expected rejection ("attempted with a source that does not support
# causation... this insertion is expected to be rejected by the gate, and
# that rejection is itself the test"). The other two extend the same
# discipline to make atomic rollback provable across more than one
# mechanism, per this milestone's explicit requirement.
INVALID_CAUSES = {
    "fixture_id": "causes_without_source_span",
    "subject_id": "xerdna:gene:001",
    "object_id": "xerdna:disease:001",
    "predicate": "biolink:causes",
    "evidence_tier": "established_evidence",
    "primary_knowledge_source": "infores:hgnc",
    "source_record_id": "STUDY:CAUSE:1",
    "retrieved_at": "2026-07-10",
    # source_span deliberately omitted -- E2 must reject this
}

INVALID_NODE_NO_XREF_NO_RATIONALE = {
    "fixture_id": "node_no_xref_no_rationale",
    "xerdna_id": "xerdna:gene:invalid",
    "category": "biolink:Gene",
    "evidence_tier": "established_evidence",
    "primary_knowledge_source": "infores:hgnc",
    "source_record_id": "HGNC:9999",
    "retrieved_at": "2026-07-10",
    # xrefs and no_xref_rationale both deliberately omitted -- Rule 1 must reject this
}

INVALID_ASSOCIATION_WRONG_SCHEMA_VERSION = {
    "fixture_id": "association_wrong_schema_version",
    "subject_id": "xerdna:gene:001",
    "object_id": "xerdna:disease:001",
    "predicate": "biolink:correlated_with",
    "evidence_tier": "established_evidence",
    "primary_knowledge_source": "infores:hgnc",
    "source_record_id": "STUDY:BADVER:1",
    "retrieved_at": "2026-07-10",
    "schema_version": "0.9",  # deliberately wrong -- the gate must reject this
}

INVALID_FIXTURES = [
    INVALID_CAUSES,
    INVALID_NODE_NO_XREF_NO_RATIONALE,
    INVALID_ASSOCIATION_WRONG_SCHEMA_VERSION,
]
