"""
The Insertion Gate -- the ONLY legal way to write a node, association,
hypothesis, prediction, checked-absent record, or entity-lineage record
into XERDNA.

Traces to: DOCS/PHASE_002_DESIGN.md Section 5 (The Insertion Gate), v1.2.
Governed by: DOCS/IMPLEMENTATION_POLICY.md.

No other module in this engine writes to nodes, associations, confidence,
hypotheses, predictions, checked_absent, or entity_lineage. Every function
in this module either succeeds with a fully valid, fully provenanced record,
or raises GateValidationError and writes nothing (each insert path uses a
single transaction).

This module intentionally exposes no update_evidence_tier(), no
update_schema_version(), and no update_xerdna_id() function of any kind
(Section 5.3 point 1) -- there is no code path in this engine capable of
changing a record's tier, schema version, or canonical/primary ID after
insertion. The only way to a stronger tier is a new, linked record
(promote_prediction(), resolve_hypothesis()), per Section 5.3 point 4.
"""

import sqlite3

from GRAPH.engine import config, db

VALID_TIERS = frozenset({"established_evidence", "computational_prediction", "research_hypothesis"})
VALID_RESOLUTION_STATUSES = frozenset({"unresolved", "not_checked"})  # "resolved" is never caller-settable (Rule 4)


class GateValidationError(ValueError):
    """Raised when a record fails the Insertion Gate's checks. Nothing is written."""


def _require_foreign_keys_enabled(conn: sqlite3.Connection) -> None:
    """
    This module's own claim to be "the ONLY legal way to insert records"
    depends on referential integrity actually being enforced on the
    connection it is given -- SQLite disables foreign-key enforcement by
    default per connection (Section 3). Checked at the start of every
    public insertion entry point; fails immediately and descriptively
    rather than silently accepting an under-enforced connection.
    """
    if not db.foreign_keys_enabled(conn):
        raise GateValidationError(
            "PRAGMA foreign_keys is not enabled on this connection. The Insertion Gate "
            "requires referential integrity enforcement to be active on every connection "
            "it writes through -- open connections via GRAPH.engine.db.connect() or "
            "db.init_db(), which set this automatically, rather than a bare sqlite3.connect()."
        )


def _validate_status(status: str) -> None:
    if status != "active" and status != "retracted" and not status.startswith("superseded_by:"):
        raise GateValidationError(
            f"status must be 'active', 'retracted', or 'superseded_by:<id>'; got {status!r}"
        )


def _validate_universal(
    *,
    schema_version: str,
    evidence_tier: str,
    primary_knowledge_source: str,
    source_record_id: str,
    status: str,
) -> None:
    """
    Section 5.1, points 1-2 -- checks that apply to every tiered record
    (nodes, associations).
    """
    if schema_version != config.SUPPORTED_SCHEMA_VERSION:
        raise GateValidationError(
            f"schema_version {schema_version!r} is not supported; "
            f"this engine build only accepts {config.SUPPORTED_SCHEMA_VERSION!r}"
        )
    if evidence_tier not in VALID_TIERS:
        raise GateValidationError(f"evidence_tier must be one of {sorted(VALID_TIERS)}; got {evidence_tier!r}")
    if not primary_knowledge_source:
        raise GateValidationError("primary_knowledge_source is required and must be non-empty")
    if not source_record_id:
        raise GateValidationError("source_record_id is required and must be non-empty")
    _validate_status(status)


def _validate_superseded_by(conn: sqlite3.Connection, table: str, id_column: str, status: str) -> None:
    """
    Section 5.1 point 2 -- a 'superseded_by:<id>' status value is validated
    against an existing record ID at insert time.
    """
    if not status.startswith("superseded_by:"):
        return
    referenced_id = status.split(":", 1)[1]
    row = conn.execute(
        f"SELECT 1 FROM {table} WHERE {id_column} = ?", (referenced_id,)  # noqa: S608 -- table/id_column are fixed, not user input
    ).fetchone()
    if row is None:
        raise GateValidationError(
            f"status 'superseded_by:{referenced_id}' does not reference an existing {table} record"
        )


def _check_namespace_registered(conn: sqlite3.Connection, term: str, kind: str) -> None:
    """
    B4 / T15 -- any xerdna:-namespaced entity category or predicate must have
    a row in xerdna_namespace_registry before it may be used in any insert.
    Non-xerdna: terms (e.g. bare Biolink categories/predicates) are not
    subject to this check.
    """
    if not term.startswith("xerdna:"):
        return
    prefix = term[len("xerdna:"):]
    row = conn.execute(
        "SELECT status FROM xerdna_namespace_registry WHERE prefix = ? AND kind = ?",
        (prefix, kind),
    ).fetchone()
    if row is None:
        raise GateValidationError(
            f"{term!r} ({kind}) is not present in xerdna_namespace_registry; "
            f"register it before use (B4)"
        )
    (status,) = row
    if status != "active":
        raise GateValidationError(f"{term!r} ({kind}) is registered but not active (status={status!r})")


def insert_node(
    conn: sqlite3.Connection,
    *,
    xerdna_id: str,
    category: str,
    evidence_tier: str,
    primary_knowledge_source: str,
    source_record_id: str,
    retrieved_at: str,
    schema_version: str = config.SUPPORTED_SCHEMA_VERSION,
    aggregator_knowledge_source: str | None = None,
    status: str = "active",
    xrefs: list[tuple[str, str]] | None = None,
    no_xref_rationale: str | None = None,
) -> None:
    """
    Insert a node and its xrefs atomically. Section 4.1, 4.2, 5.1;
    Anti-Hallucination Rule 1.

    xrefs is a list of (namespace, external_id) pairs. If empty or None,
    no_xref_rationale must be provided -- an explicit, logged rationale for
    minting a canonical ID with no resolvable external origin (Rule 1).
    """
    _require_foreign_keys_enabled(conn)
    _validate_universal(
        schema_version=schema_version,
        evidence_tier=evidence_tier,
        primary_knowledge_source=primary_knowledge_source,
        source_record_id=source_record_id,
        status=status,
    )
    _validate_superseded_by(conn, "nodes", "xerdna_id", status)
    _check_namespace_registered(conn, category, "entity_type")

    xrefs = xrefs or []
    if not xrefs and not no_xref_rationale:
        raise GateValidationError(
            "a node with no xrefs must carry an explicit no_xref_rationale (Anti-Hallucination Rule 1)"
        )

    try:
        conn.execute(
            """
            INSERT INTO nodes (
                xerdna_id, category, evidence_tier, primary_knowledge_source,
                aggregator_knowledge_source, retrieved_at, source_record_id,
                status, schema_version, no_xref_rationale
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (xerdna_id, category, evidence_tier, primary_knowledge_source,
             aggregator_knowledge_source, retrieved_at, source_record_id,
             status, schema_version, no_xref_rationale),
        )
        for namespace, external_id in xrefs:
            conn.execute(
                "INSERT INTO node_xrefs (xerdna_id, namespace, external_id) VALUES (?, ?, ?)",
                (xerdna_id, namespace, external_id),
            )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise


CAUSAL_PREDICATES = frozenset({"biolink:causes"})


def insert_association(
    conn: sqlite3.Connection,
    *,
    subject_id: str,
    object_id: str,
    predicate: str,
    evidence_tier: str,
    primary_knowledge_source: str,
    source_record_id: str,
    retrieved_at: str,
    schema_version: str = config.SUPPORTED_SCHEMA_VERSION,
    qualifier: str | None = None,
    status: str = "active",
    promoted_from: int | None = None,
    source_span: str | None = None,
    confidence_type: str | None = None,
    confidence_value: str | None = None,
    confidence_basis: str | None = None,
    prediction_method: str | None = None,
    prediction_method_ontology_term: str | None = None,
    prediction_model_version: str | None = None,
    prediction_input_reference: str | None = None,
    prediction_generated_at: str | None = None,
    _commit: bool = True,
) -> int:
    """
    Insert an association. Section 4.3, 4.4, 4.6, 5.1, 5.2, 5.3 point 3;
    E2, O4.

    Tier-specific behavior:
      established_evidence -- primary_knowledge_source must be on the
        allow-list (SI1); no confidence_* argument may be supplied.
      computational_prediction -- all five prediction_* arguments are
        required (method, model_version, input_reference, generated_at;
        method_ontology_term is optional but if absent, ontology_gap is
        recorded as true -- O2), and a confidence_type is required.
      research_hypothesis -- use insert_hypothesis(), not this function
        directly (Task 6).

    Returns the new association's id.
    """
    _require_foreign_keys_enabled(conn)
    _validate_universal(
        schema_version=schema_version,
        evidence_tier=evidence_tier,
        primary_knowledge_source=primary_knowledge_source,
        source_record_id=source_record_id,
        status=status,
    )
    _validate_superseded_by(conn, "associations", "id", status)
    _check_namespace_registered(conn, predicate, "predicate")

    if predicate in CAUSAL_PREDICATES and not source_span:
        raise GateValidationError(
            f"predicate {predicate!r} requires source_span populated with the source's own "
            f"specific passage asserting causation (E2) -- a correlational finding defaults "
            f"to a weaker predicate instead"
        )

    if evidence_tier == "established_evidence":
        if primary_knowledge_source not in config.ESTABLISHED_EVIDENCE_SOURCE_ALLOWLIST:
            raise GateValidationError(
                f"{primary_knowledge_source!r} is not on the established_evidence source "
                f"allow-list (Section 5.2, SI1)"
            )
        if confidence_type is not None or confidence_value is not None:
            raise GateValidationError(
                "established_evidence records may not carry a confidence row (Confidence Model)"
            )

    if evidence_tier == "research_hypothesis" and confidence_type not in (None, "qualitative"):
        raise GateValidationError(
            "research_hypothesis confidence is always qualitative (never numeric) at this phase"
        )

    if evidence_tier == "computational_prediction":
        missing = [
            name for name, value in (
                ("prediction_method", prediction_method),
                ("prediction_model_version", prediction_model_version),
                ("prediction_input_reference", prediction_input_reference),
                ("prediction_generated_at", prediction_generated_at),
            ) if not value
        ]
        if missing:
            raise GateValidationError(
                f"computational_prediction requires {', '.join(missing)} (Prediction Model)"
            )
        if confidence_type is None:
            raise GateValidationError(
                "computational_prediction requires a confidence_type (Confidence Model)"
            )

    if promoted_from is not None:
        row = conn.execute(
            "SELECT evidence_tier FROM associations WHERE id = ?", (promoted_from,)
        ).fetchone()
        if row is None:
            raise GateValidationError(f"promoted_from={promoted_from} does not reference an existing association")
        (referenced_tier,) = row
        if referenced_tier != "computational_prediction":
            raise GateValidationError(
                f"promoted_from must reference a computational_prediction-tier association; "
                f"referenced association {promoted_from} is tier {referenced_tier!r} (Section 5.3 point 3)"
            )

    try:
        cur = conn.execute(
            """
            INSERT INTO associations (
                subject_id, object_id, predicate, qualifier, evidence_tier,
                primary_knowledge_source, source_record_id, retrieved_at,
                status, schema_version, promoted_from, source_span
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (subject_id, object_id, predicate, qualifier, evidence_tier,
             primary_knowledge_source, source_record_id, retrieved_at,
             status, schema_version, promoted_from, source_span),
        )
        association_id = cur.lastrowid
        if evidence_tier == "computational_prediction":
            ontology_gap = 0 if prediction_method_ontology_term else 1
            conn.execute(
                """
                INSERT INTO predictions (
                    association_id, method, method_ontology_term, ontology_gap,
                    model_version, input_reference, generated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (association_id, prediction_method, prediction_method_ontology_term, ontology_gap,
                 prediction_model_version, prediction_input_reference, prediction_generated_at),
            )
        if confidence_type is not None:
            if confidence_type == "qualitative" and not confidence_basis:
                raise GateValidationError(
                    "confidence_type='qualitative' requires a non-empty confidence_basis "
                    "(Anti-Hallucination Rule 6)"
                )
            conn.execute(
                "INSERT INTO confidence (association_id, confidence_type, value, basis) VALUES (?, ?, ?, ?)",
                (association_id, confidence_type, confidence_value, confidence_basis),
            )
        if _commit:
            conn.commit()
        return association_id
    except (sqlite3.IntegrityError, GateValidationError):
        conn.rollback()
        raise


def insert_hypothesis(
    conn: sqlite3.Connection,
    *,
    subject_id: str,
    object_id: str,
    predicate: str,
    primary_knowledge_source: str,
    source_record_id: str,
    retrieved_at: str,
    claim: str,
    supporting_evidence: str,
    reasoning: str,
    generated_by: str,
    confidence_basis: str,
    contradicting_evidence: str | None = None,
    none_found_as_of: str | None = None,
    schema_version: str = config.SUPPORTED_SCHEMA_VERSION,
    qualifier: str | None = None,
    status: str = "active",
) -> int:
    """
    Insert a research_hypothesis-tier association and its hypotheses row,
    atomically. Section 4.5, 5.2 (research_hypothesis); H2, H4.

    contradicting_evidence must be provided, or none_found_as_of must be --
    absence of contradiction is a recorded state, never a silent omission.

    Returns the new association's id (== hypotheses.association_id).
    """
    _require_foreign_keys_enabled(conn)
    if not claim:
        raise GateValidationError("claim is required (Hypothesis Model)")
    if not supporting_evidence:
        raise GateValidationError("supporting_evidence is required, even if an explicit empty list (Hypothesis Model)")
    if not contradicting_evidence and not none_found_as_of:
        raise GateValidationError(
            "contradicting_evidence is required unless none_found_as_of is explicitly set (Hypothesis Model)"
        )
    if not reasoning:
        raise GateValidationError("reasoning is required (VISION.md Article VI Rule 4)")
    if not generated_by:
        raise GateValidationError("generated_by is required (Hypothesis Model)")

    try:
        association_id = insert_association(
            conn,
            subject_id=subject_id, object_id=object_id, predicate=predicate,
            evidence_tier="research_hypothesis",
            primary_knowledge_source=primary_knowledge_source, source_record_id=source_record_id,
            retrieved_at=retrieved_at, schema_version=schema_version, qualifier=qualifier, status=status,
            confidence_type="qualitative", confidence_basis=confidence_basis,
            _commit=False,
        )
        conn.execute(
            """
            INSERT INTO hypotheses (
                association_id, claim, supporting_evidence, contradicting_evidence,
                none_found_as_of, reasoning, generated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (association_id, claim, supporting_evidence, contradicting_evidence,
             none_found_as_of, reasoning, generated_by),
        )
        conn.commit()
        return association_id
    except (sqlite3.IntegrityError, GateValidationError):
        conn.rollback()
        raise


def promote_prediction(
    conn: sqlite3.Connection,
    *,
    prediction_association_id: int,
    subject_id: str,
    object_id: str,
    predicate: str,
    primary_knowledge_source: str,
    source_record_id: str,
    retrieved_at: str,
    schema_version: str = config.SUPPORTED_SCHEMA_VERSION,
    qualifier: str | None = None,
    status: str = "active",
) -> int:
    """
    The only path from computational_prediction to established_evidence.
    Section 5.3 points 3-4; Prediction Model.

    Inserts a NEW established_evidence association, with its own full
    provenance, linked via promoted_from to prediction_association_id. The
    original prediction is never touched -- both remain independently
    queryable. Rejects if prediction_association_id does not reference an
    existing computational_prediction-tier association (enforced inside
    insert_association()'s promoted_from check).

    Returns the new established_evidence association's id.
    """
    _require_foreign_keys_enabled(conn)
    return insert_association(
        conn,
        subject_id=subject_id, object_id=object_id, predicate=predicate,
        evidence_tier="established_evidence",
        primary_knowledge_source=primary_knowledge_source, source_record_id=source_record_id,
        retrieved_at=retrieved_at, schema_version=schema_version, qualifier=qualifier, status=status,
        promoted_from=prediction_association_id,
    )


def resolve_hypothesis(
    conn: sqlite3.Connection,
    *,
    hypothesis_association_id: int,
    new_status: str,
    subject_id: str,
    object_id: str,
    predicate: str,
    primary_knowledge_source: str,
    source_record_id: str,
    retrieved_at: str,
    schema_version: str = config.SUPPORTED_SCHEMA_VERSION,
    qualifier: str | None = None,
) -> int:
    """
    The only path for a research_hypothesis to become resolved -- distinct
    from promote_prediction(), never interchanged. Section 4.5
    (resolved_by), Section 5.3 points 3-4; H1, H4.

    Inserts a NEW established_evidence association (the experiment's
    finding) and links it via hypotheses.resolved_by, atomically
    transitioning hypotheses.status to new_status. The original hypothesis
    association is never touched -- both remain independently queryable.
    The resolved_by tier-restriction (Section 5.3 point 3) is satisfied by
    construction: this function always creates the linked record fresh as
    established_evidence, never accepts a pre-existing association id for it.

    Returns the new established_evidence association's id.
    """
    _require_foreign_keys_enabled(conn)
    if new_status not in ("refuted", "supported_by_experiment"):
        raise GateValidationError(
            "resolve_hypothesis() only transitions status to 'refuted' or 'supported_by_experiment' (H4)"
        )
    row = conn.execute(
        "SELECT evidence_tier FROM associations WHERE id = ?", (hypothesis_association_id,)
    ).fetchone()
    if row is None:
        raise GateValidationError(f"hypothesis_association_id={hypothesis_association_id} does not exist")
    (tier,) = row
    if tier != "research_hypothesis":
        raise GateValidationError(
            f"hypothesis_association_id={hypothesis_association_id} is tier {tier!r}, not research_hypothesis"
        )
    if conn.execute(
        "SELECT 1 FROM hypotheses WHERE association_id = ?", (hypothesis_association_id,)
    ).fetchone() is None:
        raise GateValidationError(f"no hypotheses row found for association {hypothesis_association_id}")

    try:
        resolving_id = insert_association(
            conn,
            subject_id=subject_id, object_id=object_id, predicate=predicate,
            evidence_tier="established_evidence",
            primary_knowledge_source=primary_knowledge_source, source_record_id=source_record_id,
            retrieved_at=retrieved_at, schema_version=schema_version, qualifier=qualifier,
            _commit=False,
        )
        conn.execute(
            "UPDATE hypotheses SET status = ?, resolved_by = ? WHERE association_id = ?",
            (new_status, resolving_id, hypothesis_association_id),
        )
        conn.commit()
        return resolving_id
    except (sqlite3.IntegrityError, GateValidationError):
        conn.rollback()
        raise


def insert_checked_absent(
    conn: sqlite3.Connection,
    *,
    subject: str,
    predicate: str,
    object: str,  # noqa: A002 -- matches Section 4.7's field name exactly
    checked_by: str,
    checked_at: str,
    scope: str,
) -> int:
    """
    Insert a checked_absent record. Section 4.7, 5.1 point 3; P1.

    Deliberately does NOT go through _validate_universal() -- checked_absent
    records carry no evidence_tier and are not associations (see
    GRAPH/SCHEMA.md's v1.2 Checked-Absent Records exemption rule and
    PHASE_002_DESIGN.md Section 4.7). Only its own required-field set
    (subject/predicate/object/checked_by/checked_at/scope) applies.

    Returns the new record's id.
    """
    _require_foreign_keys_enabled(conn)
    for name, value in (
        ("subject", subject), ("predicate", predicate), ("object", object),
        ("checked_by", checked_by), ("checked_at", checked_at), ("scope", scope),
    ):
        if not value:
            raise GateValidationError(f"{name} is required for a checked_absent record")

    cur = conn.execute(
        """
        INSERT INTO checked_absent (subject, predicate, object, checked_by, checked_at, scope)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (subject, predicate, object, checked_by, checked_at, scope),
    )
    conn.commit()
    return cur.lastrowid


def insert_entity_lineage(
    conn: sqlite3.Connection,
    *,
    old_xerdna_id: str,
    new_xerdna_id: str,
    relation: str,
    recorded_at: str,
) -> int:
    """
    Record a split or merge. Section 4.8, 5.1; R2; B4/T15.

    relation must be 'split_into' or 'merged_from' -- both are xerdna:
    predicates (GRAPH/SCHEMA.md Entity Identity section) and are subject to
    the Namespace Registry check the same as any other xerdna: term (B4),
    checked here as xerdna:<relation>.

    The old node's own row is never deleted -- only its `status` transitions
    (a separate, caller-driven operation on `nodes`, not performed here);
    this function only records the lineage link.

    Returns the new entity_lineage record's id.
    """
    _require_foreign_keys_enabled(conn)
    if relation not in ("split_into", "merged_from"):
        raise GateValidationError("relation must be 'split_into' or 'merged_from' (R2)")
    _check_namespace_registered(conn, f"xerdna:{relation}", "predicate")

    cur = conn.execute(
        """
        INSERT INTO entity_lineage (old_xerdna_id, new_xerdna_id, relation, recorded_at)
        VALUES (?, ?, ?, ?)
        """,
        (old_xerdna_id, new_xerdna_id, relation, recorded_at),
    )
    conn.commit()
    return cur.lastrowid
