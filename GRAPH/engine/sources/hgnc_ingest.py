"""
Loads the cached HGNC fixture into the database, exclusively through
GRAPH.engine.gate.insert_node().

Traces to: this milestone's own goal -- a controlled, local-only ingestion
path for one real, authoritative source. Reads only
GRAPH/engine/sources/fixtures/hgnc_sample.json; never imports
hgnc_fetch.py; performs no network access.
"""

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from GRAPH.engine import gate
from GRAPH.engine.sources.hgnc_mapper import SourceRecordInvalid, map_hgnc_record_to_node_kwargs

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "hgnc_sample.json"


@dataclass
class HgncIngestionReport:
    loaded: list[str] = field(default_factory=list)  # xerdna_ids successfully inserted
    mapper_rejections: list[tuple[str, str]] = field(default_factory=list)  # (identifier, reason)
    gate_rejections: list[tuple[str, str]] = field(default_factory=list)  # (identifier, reason)


def load_hgnc_fixture(conn: sqlite3.Connection, fixture_path: Path = FIXTURE_PATH) -> HgncIngestionReport:
    """
    Load every record in the cached HGNC fixture. Each record is mapped and
    validated (GRAPH.engine.sources.hgnc_mapper) before being attempted
    through the gate (GRAPH.engine.gate.insert_node()) -- a record can fail
    at either stage, and the two are reported separately so it is always
    clear whether a rejection came from the source data itself being
    unusable, or from XERDNA's own constitutional rules.
    """
    report = HgncIngestionReport()
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    retrieved_at = fixture["fetched_at"]

    for record in fixture["docs"]:
        identifier = record.get("hgnc_id") or record.get("symbol") or "<unidentified record>"
        try:
            kwargs = map_hgnc_record_to_node_kwargs(record, retrieved_at)
        except SourceRecordInvalid as exc:
            report.mapper_rejections.append((identifier, str(exc)))
            continue

        try:
            gate.insert_node(conn, **kwargs)
        except (gate.GateValidationError, sqlite3.IntegrityError) as exc:
            # IntegrityError included alongside GateValidationError: a
            # storage-layer rejection (e.g. a duplicate xerdna_id from
            # re-running this loader) is still a rejected record, not a
            # crash -- gate.insert_node() has already rolled back its own
            # transaction by the time this exception reaches here.
            report.gate_rejections.append((identifier, str(exc)))
            continue

        report.loaded.append(kwargs["xerdna_id"])

    return report
