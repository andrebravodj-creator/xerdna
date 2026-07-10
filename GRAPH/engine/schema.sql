-- XERDNA Universal Biological Memory Engine -- Storage Structure DDL
--
-- Traces to: DOCS/PHASE_002_DESIGN.md Section 4 (Storage Structure), v1.2.
-- Implements the 9 tables described there as literal SQLite DDL.
--
-- Scope boundary (Milestone 001): this file originally implemented
-- single-row/single-table constraints only. Milestone 002 (Engineering
-- Milestone 002 -- The Insertion Gate) adds the immutability triggers
-- deferred at that time (Section 5.3 point 2, below). The
-- promoted_from/resolved_by tier-restriction check (Section 5.3 point 3)
-- and the "confidence forbidden if established_evidence" rule are
-- implemented in GRAPH/engine/gate.py (application layer), per the
-- design's own "the gate looks up..." phrasing for point 3 and the
-- Confidence Model's "enforced at the storage layer... via the gate"
-- framing being satisfiable at either layer -- the gate is the layer
-- chosen here, consistent with every other cross-table rule in Section 5.
--
-- Statements are idempotent (IF NOT EXISTS) so init_db() may be called
-- safely against an existing database.

-- 4.1 nodes
CREATE TABLE IF NOT EXISTS nodes (
    xerdna_id                    TEXT PRIMARY KEY,
    category                     TEXT NOT NULL,
    evidence_tier                TEXT NOT NULL
        CHECK (evidence_tier IN ('established_evidence', 'computational_prediction', 'research_hypothesis')),
    primary_knowledge_source     TEXT NOT NULL,
    aggregator_knowledge_source  TEXT,
    retrieved_at                 TEXT NOT NULL,
    source_record_id             TEXT NOT NULL,
    status                       TEXT NOT NULL DEFAULT 'active'
        CHECK (status = 'active' OR status = 'retracted' OR status LIKE 'superseded_by:%'),
    schema_version                TEXT NOT NULL,
    no_xref_rationale            TEXT
);

-- 4.2 node_xrefs
CREATE TABLE IF NOT EXISTS node_xrefs (
    xerdna_id    TEXT NOT NULL REFERENCES nodes(xerdna_id),
    namespace    TEXT NOT NULL,
    external_id  TEXT NOT NULL,
    PRIMARY KEY (xerdna_id, namespace, external_id)
);

-- 4.3 associations
-- Note: aggregator_knowledge_source is intentionally absent -- Section 4.3's
-- field list does not name it for this table (see the design-gap note in
-- the Milestone 001 implementation plan).
CREATE TABLE IF NOT EXISTS associations (
    id                         INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id                 TEXT NOT NULL REFERENCES nodes(xerdna_id),
    object_id                  TEXT NOT NULL REFERENCES nodes(xerdna_id),
    predicate                  TEXT NOT NULL,
    qualifier                  TEXT,
    evidence_tier              TEXT NOT NULL
        CHECK (evidence_tier IN ('established_evidence', 'computational_prediction', 'research_hypothesis')),
    primary_knowledge_source   TEXT NOT NULL,
    source_record_id           TEXT NOT NULL,
    retrieved_at                TEXT NOT NULL,
    status                      TEXT NOT NULL DEFAULT 'active'
        CHECK (status = 'active' OR status = 'retracted' OR status LIKE 'superseded_by:%'),
    schema_version               TEXT NOT NULL,
    promoted_from               INTEGER REFERENCES associations(id),
    source_span                 TEXT,
    resolution_status           TEXT NOT NULL DEFAULT 'not_checked'
        CHECK (resolution_status IN ('resolved', 'unresolved', 'not_checked'))
);

-- 4.4 confidence
CREATE TABLE IF NOT EXISTS confidence (
    association_id  INTEGER PRIMARY KEY REFERENCES associations(id),
    confidence_type TEXT CHECK (confidence_type IN ('numeric', 'qualitative') OR confidence_type IS NULL),
    value           TEXT,
    basis           TEXT
);

-- 4.5 hypotheses
CREATE TABLE IF NOT EXISTS hypotheses (
    association_id          INTEGER PRIMARY KEY REFERENCES associations(id),
    claim                    TEXT NOT NULL,
    supporting_evidence     TEXT NOT NULL,
    contradicting_evidence  TEXT,
    none_found_as_of        TEXT,
    reasoning                TEXT NOT NULL,
    status                   TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'under_investigation', 'refuted', 'supported_by_experiment')),
    generated_by             TEXT NOT NULL,
    resolved_by              INTEGER REFERENCES associations(id),
    CHECK (contradicting_evidence IS NOT NULL OR none_found_as_of IS NOT NULL)
);

-- 4.6 predictions
CREATE TABLE IF NOT EXISTS predictions (
    association_id        INTEGER PRIMARY KEY REFERENCES associations(id),
    method                 TEXT NOT NULL,
    method_ontology_term  TEXT,
    ontology_gap           INTEGER NOT NULL DEFAULT 0 CHECK (ontology_gap IN (0, 1)),
    model_version          TEXT NOT NULL,
    input_reference        TEXT NOT NULL,
    generated_at           TEXT NOT NULL,
    CHECK (method_ontology_term IS NOT NULL OR ontology_gap = 1)
);

-- 4.7 checked_absent
-- No evidence_tier column, by design -- this is the storage-layer expression
-- of the exemption stated in GRAPH/SCHEMA.md v1.2's Checked-Absent Records
-- rule and PHASE_002_DESIGN.md Section 4.7.
CREATE TABLE IF NOT EXISTS checked_absent (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    subject      TEXT NOT NULL,
    predicate    TEXT NOT NULL,
    object       TEXT NOT NULL,
    checked_by   TEXT NOT NULL,
    checked_at   TEXT NOT NULL,
    scope        TEXT NOT NULL
);

-- 4.8 entity_lineage
CREATE TABLE IF NOT EXISTS entity_lineage (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    old_xerdna_id  TEXT NOT NULL REFERENCES nodes(xerdna_id),
    new_xerdna_id  TEXT NOT NULL REFERENCES nodes(xerdna_id),
    relation        TEXT NOT NULL CHECK (relation IN ('split_into', 'merged_from')),
    recorded_at     TEXT NOT NULL
);

-- 4.9 xerdna_namespace_registry
CREATE TABLE IF NOT EXISTS xerdna_namespace_registry (
    prefix         TEXT PRIMARY KEY,
    kind           TEXT NOT NULL CHECK (kind IN ('entity_type', 'predicate')),
    parent_type    TEXT,
    introduced_in  TEXT NOT NULL,
    rationale      TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'deprecated'))
);

-- Section 5.3 point 2 -- immutability, storage layer, defense in depth.
-- Once inserted, evidence_tier, schema_version, and the identifying column
-- (xerdna_id on nodes, id on associations) may never be modified, even by a
-- direct, ad hoc database edit that bypasses the application-layer gate
-- (which itself exposes no update function for any of them -- point 1).

CREATE TRIGGER IF NOT EXISTS trg_nodes_immutable_evidence_tier
BEFORE UPDATE OF evidence_tier ON nodes
WHEN OLD.evidence_tier != NEW.evidence_tier
BEGIN
    SELECT RAISE(ABORT, 'nodes.evidence_tier is immutable after insert');
END;

CREATE TRIGGER IF NOT EXISTS trg_nodes_immutable_schema_version
BEFORE UPDATE OF schema_version ON nodes
WHEN OLD.schema_version != NEW.schema_version
BEGIN
    SELECT RAISE(ABORT, 'nodes.schema_version is immutable after insert');
END;

CREATE TRIGGER IF NOT EXISTS trg_nodes_immutable_xerdna_id
BEFORE UPDATE OF xerdna_id ON nodes
WHEN OLD.xerdna_id != NEW.xerdna_id
BEGIN
    SELECT RAISE(ABORT, 'nodes.xerdna_id is immutable after insert');
END;

CREATE TRIGGER IF NOT EXISTS trg_associations_immutable_evidence_tier
BEFORE UPDATE OF evidence_tier ON associations
WHEN OLD.evidence_tier != NEW.evidence_tier
BEGIN
    SELECT RAISE(ABORT, 'associations.evidence_tier is immutable after insert');
END;

CREATE TRIGGER IF NOT EXISTS trg_associations_immutable_schema_version
BEFORE UPDATE OF schema_version ON associations
WHEN OLD.schema_version != NEW.schema_version
BEGIN
    SELECT RAISE(ABORT, 'associations.schema_version is immutable after insert');
END;

CREATE TRIGGER IF NOT EXISTS trg_associations_immutable_id
BEFORE UPDATE OF id ON associations
WHEN OLD.id != NEW.id
BEGIN
    SELECT RAISE(ABORT, 'associations.id is immutable after insert');
END;
