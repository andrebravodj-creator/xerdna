"""
Validation framework for Engineering Milestone 004 -- HGNC Ingestion Path.

Traces to: this milestone's own kickoff (HGNC gene records, one real
authoritative source). Every test in this file runs entirely offline --
GRAPH/engine/sources/hgnc_fetch.py is never imported here.

Standard library only (unittest), consistent with prior milestones.
"""

import inspect
import json
import tempfile
import unittest
from pathlib import Path

from GRAPH.engine import config, db, gate
from GRAPH.engine.sources import hgnc_ingest, hgnc_mapper


FIXTURE_PATH = Path(__file__).resolve().parent.parent / "sources" / "fixtures" / "hgnc_sample.json"


class IngestTestCase(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test_engine.db"
        self.conn = db.init_db(self.db_path)

    def tearDown(self):
        self.conn.close()
        self._tmpdir.cleanup()


def _write_fixture_with_corruption(tmpdir: Path) -> Path:
    """
    A copy of the real fixture plus one deliberately-corrupted 4th record
    (missing hgnc_id) -- kept separate from the real, committed fixture so
    that file stays an unmodified record of what HGNC actually returned.
    """
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    corrupted = dict(fixture["docs"][0])
    corrupted["symbol"] = "CORRUPTED-TEST-RECORD"
    del corrupted["hgnc_id"]
    fixture = dict(fixture)
    fixture["docs"] = [*fixture["docs"], corrupted]
    path = tmpdir / "hgnc_sample_with_corruption.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")
    return path


# --- Task 1: fixture presence and shape ---

class TestHgncFixture(unittest.TestCase):
    def test_fixture_file_exists(self):
        self.assertTrue(FIXTURE_PATH.exists())

    def test_fixture_has_three_real_docs(self):
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(fixture["docs"]), 3)
        symbols = {doc["symbol"] for doc in fixture["docs"]}
        self.assertEqual(symbols, {"BRCA1", "TP53", "EGFR"})

    def test_fixture_records_are_all_approved(self):
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        for doc in fixture["docs"]:
            with self.subTest(symbol=doc["symbol"]):
                self.assertEqual(doc["status"], "Approved")

    def test_fixture_has_provenance_metadata(self):
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        for key in ("source", "source_url", "access_method", "fetched_at"):
            with self.subTest(key=key):
                self.assertIn(key, fixture)

    def test_no_network_module_imported_by_this_test_file(self):
        """hgnc_fetch.py (the only file with network access) is never imported here."""
        source = inspect.getsource(__import__(__name__))
        self.assertNotIn("hgnc_fetch", source)


# --- Task 2: field mapping + validation ---

class TestHgncMapper(unittest.TestCase):
    def setUp(self):
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.docs_by_symbol = {doc["symbol"]: doc for doc in fixture["docs"]}
        self.retrieved_at = fixture["fetched_at"]

    def test_brca1_maps_correctly(self):
        kwargs = hgnc_mapper.map_hgnc_record_to_node_kwargs(self.docs_by_symbol["BRCA1"], self.retrieved_at)
        self.assertEqual(kwargs["xerdna_id"], "xerdna:gene:hgnc-1100")
        self.assertEqual(kwargs["category"], "biolink:Gene")
        self.assertEqual(kwargs["evidence_tier"], "established_evidence")
        self.assertEqual(kwargs["primary_knowledge_source"], "infores:hgnc")
        self.assertEqual(kwargs["source_record_id"], "HGNC:1100")
        self.assertEqual(kwargs["schema_version"], config.SUPPORTED_SCHEMA_VERSION)
        xref_namespaces = {ns for ns, _ in kwargs["xrefs"]}
        self.assertIn("HGNC", xref_namespaces)
        self.assertIn("NCBIGene", xref_namespaces)  # BRCA1 has entrez_id=672
        self.assertIn(("NCBIGene", "672"), kwargs["xrefs"])

    def test_all_three_real_records_map_without_error(self):
        for symbol, doc in self.docs_by_symbol.items():
            with self.subTest(symbol=symbol):
                kwargs = hgnc_mapper.map_hgnc_record_to_node_kwargs(doc, self.retrieved_at)
                self.assertTrue(kwargs["xerdna_id"].startswith("xerdna:gene:hgnc-"))

    def test_missing_hgnc_id_rejected(self):
        record = dict(self.docs_by_symbol["BRCA1"])
        del record["hgnc_id"]
        with self.assertRaises(hgnc_mapper.SourceRecordInvalid):
            hgnc_mapper.map_hgnc_record_to_node_kwargs(record, self.retrieved_at)

    def test_missing_symbol_rejected(self):
        record = dict(self.docs_by_symbol["BRCA1"])
        del record["symbol"]
        with self.assertRaises(hgnc_mapper.SourceRecordInvalid):
            hgnc_mapper.map_hgnc_record_to_node_kwargs(record, self.retrieved_at)

    def test_non_approved_status_rejected(self):
        record = dict(self.docs_by_symbol["BRCA1"])
        record["status"] = "Entry Withdrawn"
        with self.assertRaises(hgnc_mapper.SourceRecordInvalid):
            hgnc_mapper.map_hgnc_record_to_node_kwargs(record, self.retrieved_at)

    def test_record_with_no_secondary_xrefs_still_maps(self):
        """A record with only hgnc_id (no entrez/ensembl/uniprot) still satisfies Rule 1 via the HGNC xref alone."""
        record = {"hgnc_id": "HGNC:99999", "symbol": "TESTGENE", "status": "Approved"}
        kwargs = hgnc_mapper.map_hgnc_record_to_node_kwargs(record, self.retrieved_at)
        self.assertEqual(kwargs["xrefs"], [("HGNC", "99999")])


# --- Task 3: ingestion loader ---

class TestLoadHgncFixture(IngestTestCase):
    def test_all_three_real_records_loaded(self):
        report = hgnc_ingest.load_hgnc_fixture(self.conn)
        self.assertEqual(len(report.loaded), 3)
        self.assertEqual(report.mapper_rejections, [])
        self.assertEqual(report.gate_rejections, [])
        for xerdna_id in ("xerdna:gene:hgnc-1100", "xerdna:gene:hgnc-11998", "xerdna:gene:hgnc-3236"):
            with self.subTest(node=xerdna_id):
                row = self.conn.execute("SELECT 1 FROM nodes WHERE xerdna_id = ?", (xerdna_id,)).fetchone()
                self.assertIsNotNone(row)

    def test_corrupted_record_rejected_without_affecting_valid_ones(self):
        corrupted_path = _write_fixture_with_corruption(Path(self._tmpdir.name))
        report = hgnc_ingest.load_hgnc_fixture(self.conn, fixture_path=corrupted_path)
        self.assertEqual(len(report.loaded), 3)
        self.assertEqual(len(report.mapper_rejections), 1)
        identifier, reason = report.mapper_rejections[0]
        self.assertEqual(identifier, "CORRUPTED-TEST-RECORD")
        self.assertIn("hgnc_id", reason)
        self.assertEqual(report.gate_rejections, [])


# --- Task 4: full validation ---

ALL_TABLES = (
    "nodes", "node_xrefs", "associations", "confidence", "hypotheses",
    "predictions", "checked_absent", "entity_lineage", "xerdna_namespace_registry",
)


def _snapshot(conn) -> dict:
    return {
        table: sorted(conn.execute(f"SELECT * FROM {table}").fetchall())  # noqa: S608 -- ALL_TABLES is a fixed tuple
        for table in ALL_TABLES
    }


class TestNoNetworkAccessInTestedPath(unittest.TestCase):
    """
    Structural proof, not just a claim: neither hgnc_mapper.py nor
    hgnc_ingest.py -- the two modules Milestone 004's tests actually
    exercise -- import any networking capability. hgnc_fetch.py is
    permitted to (and does); it is checked separately, by name, never to
    be imported from the other two.
    """

    @staticmethod
    def _import_lines(module) -> list[str]:
        return [
            line.strip() for line in inspect.getsource(module).splitlines()
            if line.strip().startswith(("import ", "from "))
        ]

    def test_mapper_has_no_networking_imports(self):
        import_lines = self._import_lines(hgnc_mapper)
        for forbidden in ("urllib", "requests", "socket", "http.client", "hgnc_fetch"):
            with self.subTest(forbidden=forbidden):
                self.assertFalse(any(forbidden in line for line in import_lines))

    def test_ingest_has_no_networking_imports(self):
        import_lines = self._import_lines(hgnc_ingest)
        for forbidden in ("urllib", "requests", "socket", "http.client", "hgnc_fetch"):
            with self.subTest(forbidden=forbidden):
                self.assertFalse(any(forbidden in line for line in import_lines))

    def test_fetch_module_is_never_imported_by_mapper_or_ingest(self):
        # redundant with the substring checks above, phrased as an explicit
        # module-identity check for extra confidence
        import GRAPH.engine.sources.hgnc_ingest as ingest_mod
        import GRAPH.engine.sources.hgnc_mapper as mapper_mod
        self.assertNotIn("hgnc_fetch", dir(ingest_mod))
        self.assertNotIn("hgnc_fetch", dir(mapper_mod))


class TestFieldMappingAgainstRealValues(unittest.TestCase):
    """Spot-checks mapped output against the actual real values fetched from HGNC, not synthetic stand-ins."""

    def setUp(self):
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.docs_by_symbol = {doc["symbol"]: doc for doc in fixture["docs"]}
        self.retrieved_at = fixture["fetched_at"]

    def test_tp53_real_values_preserved(self):
        kwargs = hgnc_mapper.map_hgnc_record_to_node_kwargs(self.docs_by_symbol["TP53"], self.retrieved_at)
        self.assertEqual(kwargs["xerdna_id"], "xerdna:gene:hgnc-11998")
        self.assertEqual(kwargs["source_record_id"], "HGNC:11998")
        self.assertIn(("NCBIGene", "7157"), kwargs["xrefs"])  # TP53's real, verified Entrez ID

    def test_egfr_real_values_preserved(self):
        kwargs = hgnc_mapper.map_hgnc_record_to_node_kwargs(self.docs_by_symbol["EGFR"], self.retrieved_at)
        self.assertEqual(kwargs["xerdna_id"], "xerdna:gene:hgnc-3236")
        self.assertEqual(kwargs["source_record_id"], "HGNC:3236")
        self.assertIn(("NCBIGene", "1956"), kwargs["xrefs"])  # EGFR's real, verified Entrez ID

    def test_retrieved_at_matches_actual_fetch_timestamp(self):
        kwargs = hgnc_mapper.map_hgnc_record_to_node_kwargs(self.docs_by_symbol["BRCA1"], self.retrieved_at)
        self.assertEqual(kwargs["retrieved_at"], self.retrieved_at)


class TestProvenancePreservedEndToEnd(IngestTestCase):
    def test_every_loaded_node_has_correct_tier_and_provenance(self):
        hgnc_ingest.load_hgnc_fixture(self.conn)
        rows = self.conn.execute(
            "SELECT xerdna_id, evidence_tier, primary_knowledge_source, source_record_id, schema_version FROM nodes"
        ).fetchall()
        self.assertEqual(len(rows), 3)
        for xerdna_id, tier, source, source_id, schema_version in rows:
            with self.subTest(node=xerdna_id):
                self.assertEqual(tier, "established_evidence")
                self.assertEqual(source, "infores:hgnc")
                self.assertTrue(source_id.startswith("HGNC:"))
                self.assertEqual(schema_version, config.SUPPORTED_SCHEMA_VERSION)

    def test_every_loaded_node_has_at_least_the_hgnc_xref(self):
        hgnc_ingest.load_hgnc_fixture(self.conn)
        for xerdna_id in ("xerdna:gene:hgnc-1100", "xerdna:gene:hgnc-11998", "xerdna:gene:hgnc-3236"):
            with self.subTest(node=xerdna_id):
                count = self.conn.execute(
                    "SELECT COUNT(*) FROM node_xrefs WHERE xerdna_id = ? AND namespace = 'HGNC'", (xerdna_id,)
                ).fetchone()[0]
                self.assertEqual(count, 1)


class TestAtomicRollback(IngestTestCase):
    """
    Full 9-table before/after snapshots around each kind of failure this
    milestone can produce: a mapper-level rejection (never reaches the
    gate at all) and a gate/storage-level rejection (reaches the gate,
    fails, must roll back completely).
    """

    def test_mapper_rejection_leaves_no_trace(self):
        record = {"hgnc_id": "HGNC:1100", "symbol": "BRCA1", "status": "Withdrawn"}
        before = _snapshot(self.conn)
        with self.assertRaises(hgnc_mapper.SourceRecordInvalid):
            hgnc_mapper.map_hgnc_record_to_node_kwargs(record, "2026-07-10")
        after = _snapshot(self.conn)
        self.assertEqual(before, after)

    def test_duplicate_insert_gate_rejection_leaves_no_trace_beyond_the_original(self):
        hgnc_ingest.load_hgnc_fixture(self.conn)  # first load: 3 real nodes land
        before = _snapshot(self.conn)
        report = hgnc_ingest.load_hgnc_fixture(self.conn)  # second load: all 3 are now duplicates
        after = _snapshot(self.conn)
        self.assertEqual(before, after)  # no new rows, no partial rows, no corruption
        self.assertEqual(len(report.gate_rejections), 3)
        self.assertEqual(report.loaded, [])

    def test_corrupted_record_pass_leaves_valid_records_exactly_as_they_were(self):
        hgnc_ingest.load_hgnc_fixture(self.conn)
        before = _snapshot(self.conn)
        corrupted_path = _write_fixture_with_corruption(Path(self._tmpdir.name))
        # loading a fixture with 3 already-duplicate + 1 corrupted record:
        # every one of the 4 must be rejected, none altering existing state
        hgnc_ingest.load_hgnc_fixture(self.conn, fixture_path=corrupted_path)
        after = _snapshot(self.conn)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
