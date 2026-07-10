"""
The controlled ingestion path for GRAPH/engine/seed_data.py's dataset.

Traces to: DOCS/PHASE_002_DESIGN.md Section 7 (Seed Data). This is
Milestone 003's own goal made concrete: prove biological records enter
XERDNA only through GRAPH/engine/gate.py's public functions.

No SQL of any kind appears in this file, with one documented exception --
see _register_namespace_entries()'s own docstring.
"""

import sqlite3
from dataclasses import dataclass, field

from GRAPH.engine import gate, seed_data


@dataclass
class IngestionReport:
    nodes_loaded: list[str] = field(default_factory=list)
    associations_loaded: dict[str, int] = field(default_factory=dict)  # fixture_id -> association_id
    prediction_id: int | None = None
    promotion_id: int | None = None
    hypothesis_id: int | None = None
    resolution_id: int | None = None
    checked_absent_id: int | None = None
    entity_lineage_id: int | None = None
    rejections: list[tuple[str, str]] = field(default_factory=list)  # (fixture_id, error message)


def _register_namespace_entries(conn: sqlite3.Connection) -> None:
    """
    The one exception to "no SQL except through gate.py" in this module:
    GRAPH/SCHEMA.md's Namespace Registry entries are Level-5 governance
    metadata about which xerdna: terms are permitted, not biological
    records -- PHASE_002_DESIGN.md Section 4.9 has no corresponding
    gate.py insert function, unlike every other table in Section 4. This
    populates the registry itself; it does not insert a biological fact
    into the graph, which is what every other call in this module does.
    """
    for entry in seed_data.NAMESPACE_REGISTRY_ENTRIES:
        conn.execute(
            """
            INSERT OR IGNORE INTO xerdna_namespace_registry
                (prefix, kind, parent_type, introduced_in, rationale)
            VALUES (?, ?, ?, ?, ?)
            """,
            (entry["prefix"], entry["kind"], entry["parent_type"],
             entry["introduced_in"], entry["rationale"]),
        )
    conn.commit()


def load_seed_dataset(conn: sqlite3.Connection) -> IngestionReport:
    """
    Load the full Milestone 003 valid seed dataset. Every biological
    record is inserted exclusively through gate.py's public functions, in
    dependency order (registry -> nodes -> associations -> prediction ->
    promotion -> hypothesis -> resolution -> checked-absent -> split).
    """
    report = IngestionReport()

    _register_namespace_entries(conn)

    for node in seed_data.NODES:
        gate.insert_node(conn, **node)
        report.nodes_loaded.append(node["xerdna_id"])

    for assoc in seed_data.VALID_ASSOCIATIONS:
        fixture_id = assoc["fixture_id"]
        kwargs = {k: v for k, v in assoc.items() if k != "fixture_id"}
        report.associations_loaded[fixture_id] = gate.insert_association(conn, **kwargs)

    report.prediction_id = gate.insert_association(conn, **seed_data.PREDICTION)
    report.promotion_id = gate.promote_prediction(
        conn, prediction_association_id=report.prediction_id, **seed_data.PREDICTION_PROMOTION
    )

    report.hypothesis_id = gate.insert_hypothesis(conn, **seed_data.HYPOTHESIS)
    report.resolution_id = gate.resolve_hypothesis(
        conn, hypothesis_association_id=report.hypothesis_id, **seed_data.HYPOTHESIS_RESOLUTION
    )

    report.checked_absent_id = gate.insert_checked_absent(conn, **seed_data.CHECKED_ABSENT)

    gate.insert_node(conn, **seed_data.ENTITY_SPLIT_NEW_NODE)
    report.entity_lineage_id = gate.insert_entity_lineage(conn, **seed_data.ENTITY_LINEAGE)

    return report


def attempt_rejected_fixtures(
    conn: sqlite3.Connection, report: IngestionReport | None = None
) -> IngestionReport:
    """
    Attempt each deliberately-invalid fixture in seed_data.INVALID_FIXTURES,
    through gate.py exclusively, expecting every one to raise
    GateValidationError. Each rejection is recorded in report.rejections.
    Whether a rejected attempt leaves the database state unchanged is
    verified separately, by test_milestone_003.py's before/after snapshots
    -- not asserted here.

    Raises RuntimeError if any fixture unexpectedly succeeds -- an
    "expected-invalid" fixture the gate accepts is itself a defect worth
    halting on, not silently ignoring.
    """
    if report is None:
        report = IngestionReport()

    for fixture in seed_data.INVALID_FIXTURES:
        fixture_id = fixture["fixture_id"]
        kwargs = {k: v for k, v in fixture.items() if k != "fixture_id"}
        try:
            if "xerdna_id" in kwargs:
                gate.insert_node(conn, **kwargs)
            else:
                gate.insert_association(conn, **kwargs)
        except gate.GateValidationError as exc:
            report.rejections.append((fixture_id, str(exc)))
        else:
            raise RuntimeError(
                f"fixture {fixture_id!r} was expected to be rejected by the gate but succeeded"
            )

    return report
