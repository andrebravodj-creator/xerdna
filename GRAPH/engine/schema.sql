-- XERDNA Universal Biological Memory Engine -- Storage Structure DDL
--
-- Traces to: DOCS/PHASE_002_DESIGN.md Section 4 (Storage Structure), v1.2.
-- Implements the 9 tables described there as literal SQLite DDL.
--
-- Scope boundary: this file implements single-row/single-table constraints
-- only (NOT NULL, CHECK, foreign keys). Cross-table rules -- immutability
-- triggers, the promoted_from/resolved_by tier-restriction check, and the
-- "confidence forbidden if established_evidence" rule -- belong to
-- Section 5 (The Insertion Gate) and are deliberately NOT implemented here;
-- they are a future engineering milestone's scope, per Milestone 001's
-- own stated boundary.
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
