"""
Validation framework for Engineering Milestone 003 -- Controlled Biological
Record Ingestion Path.

Traces to: DOCS/PHASE_002_DESIGN.md Section 7 (Seed Data). Built
incrementally, one task at a time, mirroring GRAPH/engine/seed_data.py and
GRAPH/engine/ingest.py's own construction.

Standard library only (unittest), consistent with Milestones 001 and 002.
"""

import inspect
import tempfile
import unittest
from pathlib import Path

from GRAPH.engine import config, db, gate, ingest, seed_data


class IngestTestCase(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test_engine.db"
        self.conn = db.init_db(self.db_path)

    def tearDown(self):
        self.conn.close()
        self._tmpdir.cleanup()


# --- Task 1: seed data fixtures (structural check only -- no gate calls) ---

class TestSeedDataFixtures(unittest.TestCase):
    def test_four_nodes_defined(self):
        self.assertEqual(len(seed_data.NODES), 4)

    def test_every_node_has_required_gate_keys(self):
        required = {"xerdna_id", "category", "evidence_tier", "primary_knowledge_source",
                    "source_record_id", "retrieved_at"}
        for node in seed_data.NODES:
            with self.subTest(node=node["xerdna_id"]):
                self.assertTrue(required.issubset(node.keys()))

    def test_every_node_has_xrefs(self):
        for node in seed_data.NODES:
            with self.subTest(node=node["xerdna_id"]):
                self.assertTrue(node.get("xrefs"))

    def test_two_distinct_proteins_for_interacts_with(self):
        proteins = [n for n in seed_data.NODES if n["category"] == "biolink:Protein"]
        self.assertEqual(len(proteins), 2)
        self.assertNotEqual(proteins[0]["xerdna_id"], proteins[1]["xerdna_id"])

    def test_valid_associations_defined(self):
        self.assertEqual(len(seed_data.VALID_ASSOCIATIONS), 2)
        predicates = {a["predicate"] for a in seed_data.VALID_ASSOCIATIONS}
        self.assertEqual(predicates, {"biolink:interacts_with", "biolink:correlated_with"})

    def test_prediction_has_all_required_fields(self):
        required = {"prediction_method", "prediction_model_version",
                    "prediction_input_reference", "prediction_generated_at", "confidence_type"}
        self.assertTrue(required.issubset(seed_data.PREDICTION.keys()))
        self.assertEqual(seed_data.PREDICTION["evidence_tier"], "computational_prediction")

    def test_hypothesis_spans_gene_protein_disease(self):
        claim = seed_data.HYPOTHESIS["claim"]
        for entity in ("xerdna:gene:001", "xerdna:protein:001", "xerdna:disease:001"):
            with self.subTest(entity=entity):
                self.assertIn(entity, claim)

    def test_hypothesis_none_found_as_of_present(self):
        self.assertTrue(seed_data.HYPOTHESIS.get("none_found_as_of"))
        self.assertIsNone(seed_data.HYPOTHESIS.get("contradicting_evidence"))

    def test_checked_absent_has_all_required_fields(self):
        required = {"subject", "predicate", "object", "checked_by", "checked_at", "scope"}
        self.assertTrue(required.issubset(seed_data.CHECKED_ABSENT.keys()))

    def test_entity_lineage_relation_is_split_into(self):
        self.assertEqual(seed_data.ENTITY_LINEAGE["relation"], "split_into")

    def test_namespace_registry_entry_matches_lineage_relation(self):
        prefixes = {e["prefix"] for e in seed_data.NAMESPACE_REGISTRY_ENTRIES}
        self.assertIn(seed_data.ENTITY_LINEAGE["relation"], prefixes)

    def test_three_invalid_fixtures_defined(self):
        self.assertEqual(len(seed_data.INVALID_FIXTURES), 3)
        fixture_ids = {f["fixture_id"] for f in seed_data.INVALID_FIXTURES}
        self.assertEqual(
            fixture_ids,
            {"causes_without_source_span", "node_no_xref_no_rationale", "association_wrong_schema_version"},
        )

    def test_invalid_causes_fixture_has_no_source_span(self):
        self.assertNotIn("source_span", seed_data.INVALID_CAUSES)

    def test_invalid_node_fixture_has_no_xrefs_or_rationale(self):
        self.assertNotIn("xrefs", seed_data.INVALID_NODE_NO_XREF_NO_RATIONALE)
        self.assertNotIn("no_xref_rationale", seed_data.INVALID_NODE_NO_XREF_NO_RATIONALE)

    def test_no_sql_in_seed_data_module(self):
        """seed_data.py is pure data -- no SQL keywords should appear anywhere in it."""
        source = inspect.getsource(seed_data)
        for keyword in ("INSERT INTO", "UPDATE ", "DELETE FROM", "cursor.execute", "conn.execute"):
            with self.subTest(keyword=keyword):
                self.assertNotIn(keyword, source)


# --- Task 2: ingestion loader, valid path ---

class TestLoadSeedDatasetValidPath(IngestTestCase):
    def setUp(self):
        super().setUp()
        self.report = ingest.load_seed_dataset(self.conn)

    def test_all_four_nodes_loaded(self):
        self.assertEqual(len(self.report.nodes_loaded), 4)
        for xerdna_id in ("xerdna:gene:001", "xerdna:protein:001", "xerdna:protein:002", "xerdna:disease:001"):
            with self.subTest(node=xerdna_id):
                row = self.conn.execute(
                    "SELECT 1 FROM nodes WHERE xerdna_id = ?", (xerdna_id,)
                ).fetchone()
                self.assertIsNotNone(row)

    def test_node_evidence_tier_and_provenance_preserved(self):
        row = self.conn.execute(
            "SELECT evidence_tier, primary_knowledge_source, source_record_id, schema_version "
            "FROM nodes WHERE xerdna_id = 'xerdna:gene:001'"
        ).fetchone()
        self.assertEqual(row, ("established_evidence", "infores:hgnc", "HGNC:1100", config.SUPPORTED_SCHEMA_VERSION))

    def test_node_xrefs_preserved(self):
        count = self.conn.execute(
            "SELECT COUNT(*) FROM node_xrefs WHERE xerdna_id = 'xerdna:gene:001'"
        ).fetchone()[0]
        self.assertEqual(count, 2)  # HGNC + NCBIGene, per seed_data.NODES

    def test_two_valid_associations_loaded(self):
        self.assertEqual(len(self.report.associations_loaded), 2)
        for fixture_id, assoc_id in self.report.associations_loaded.items():
            with self.subTest(fixture=fixture_id):
                tier = self.conn.execute(
                    "SELECT evidence_tier FROM associations WHERE id = ?", (assoc_id,)
                ).fetchone()[0]
                self.assertEqual(tier, "established_evidence")

    def test_prediction_loaded_and_promoted(self):
        pred_tier = self.conn.execute(
            "SELECT evidence_tier FROM associations WHERE id = ?", (self.report.prediction_id,)
        ).fetchone()[0]
        self.assertEqual(pred_tier, "computational_prediction")
        promo_tier, promoted_from = self.conn.execute(
            "SELECT evidence_tier, promoted_from FROM associations WHERE id = ?", (self.report.promotion_id,)
        ).fetchone()
        self.assertEqual(promo_tier, "established_evidence")
        self.assertEqual(promoted_from, self.report.prediction_id)

    def test_hypothesis_loaded_and_resolved(self):
        hyp_tier = self.conn.execute(
            "SELECT evidence_tier FROM associations WHERE id = ?", (self.report.hypothesis_id,)
        ).fetchone()[0]
        self.assertEqual(hyp_tier, "research_hypothesis")
        status, resolved_by = self.conn.execute(
            "SELECT status, resolved_by FROM hypotheses WHERE association_id = ?", (self.report.hypothesis_id,)
        ).fetchone()
        self.assertEqual(status, "supported_by_experiment")
        self.assertEqual(resolved_by, self.report.resolution_id)

    def test_checked_absent_loaded_with_no_tier(self):
        row = self.conn.execute(
            "SELECT subject FROM checked_absent WHERE id = ?", (self.report.checked_absent_id,)
        ).fetchone()
        self.assertIsNotNone(row)
        columns = {c[1] for c in self.conn.execute("PRAGMA table_info(checked_absent);")}
        self.assertNotIn("evidence_tier", columns)

    def test_entity_split_recorded_old_node_not_deleted(self):
        old_id, new_id = self.conn.execute(
            "SELECT old_xerdna_id, new_xerdna_id FROM entity_lineage WHERE id = ?",
            (self.report.entity_lineage_id,),
        ).fetchone()
        self.assertEqual(old_id, "xerdna:gene:001")
        self.assertEqual(new_id, "xerdna:gene:001-b")
        both_present = self.conn.execute(
            "SELECT COUNT(*) FROM nodes WHERE xerdna_id IN ('xerdna:gene:001', 'xerdna:gene:001-b')"
        ).fetchone()[0]
        self.assertEqual(both_present, 2)

    def test_schema_version_preserved_on_every_association(self):
        rows = self.conn.execute("SELECT schema_version FROM associations").fetchall()
        self.assertTrue(rows)
        for (version,) in rows:
            self.assertEqual(version, config.SUPPORTED_SCHEMA_VERSION)


# --- Task 3: ingestion loader, rejection path ---

class TestAttemptRejectedFixtures(IngestTestCase):
    def setUp(self):
        super().setUp()
        ingest.load_seed_dataset(self.conn)  # valid data first, so rejections are tested against a realistic state

    def test_all_three_invalid_fixtures_rejected(self):
        report = ingest.attempt_rejected_fixtures(self.conn)
        self.assertEqual(len(report.rejections), 3)
        rejected_ids = {fixture_id for fixture_id, _ in report.rejections}
        self.assertEqual(
            rejected_ids,
            {"causes_without_source_span", "node_no_xref_no_rationale", "association_wrong_schema_version"},
        )

    def test_rejection_messages_are_descriptive(self):
        report = ingest.attempt_rejected_fixtures(self.conn)
        messages = dict(report.rejections)
        self.assertIn("source_span", messages["causes_without_source_span"])
        self.assertIn("no_xref_rationale", messages["node_no_xref_no_rationale"])
        self.assertIn("schema_version", messages["association_wrong_schema_version"])

    def test_composes_with_a_shared_report_object(self):
        report = ingest.IngestionReport()
        ingest.attempt_rejected_fixtures(self.conn, report=report)
        self.assertEqual(len(report.rejections), 3)
        self.assertEqual(report.nodes_loaded, [])  # untouched by the rejection pass


# --- Task 4: full validation -- atomic rollback, gate-only structure, namespace integrity ---

ALL_TABLES = (
    "nodes", "node_xrefs", "associations", "confidence", "hypotheses",
    "predictions", "checked_absent", "entity_lineage", "xerdna_namespace_registry",
)


def _snapshot(conn) -> dict:
    """Full-table row-count-and-content snapshot across every table this engine defines."""
    return {
        table: sorted(conn.execute(f"SELECT * FROM {table}").fetchall())  # noqa: S608 -- ALL_TABLES is a fixed tuple
        for table in ALL_TABLES
    }


class TestAtomicRollback(IngestTestCase):
    """
    Proves atomic rollback observably, not just "no exception leaked":
    a full snapshot of every table is taken immediately before and after
    each rejected insert attempt, and must be byte-for-byte identical.
    """

    def setUp(self):
        super().setUp()
        ingest.load_seed_dataset(self.conn)  # realistic non-empty state to roll back against

    def test_causes_without_source_span_leaves_no_trace(self):
        before = _snapshot(self.conn)
        kwargs = {k: v for k, v in seed_data.INVALID_CAUSES.items() if k != "fixture_id"}
        with self.assertRaises(gate.GateValidationError):
            gate.insert_association(self.conn, **kwargs)
        after = _snapshot(self.conn)
        self.assertEqual(before, after)

    def test_node_no_xref_no_rationale_leaves_no_trace(self):
        before = _snapshot(self.conn)
        kwargs = {k: v for k, v in seed_data.INVALID_NODE_NO_XREF_NO_RATIONALE.items() if k != "fixture_id"}
        with self.assertRaises(gate.GateValidationError):
            gate.insert_node(self.conn, **kwargs)
        after = _snapshot(self.conn)
        self.assertEqual(before, after)

    def test_wrong_schema_version_leaves_no_trace(self):
        before = _snapshot(self.conn)
        kwargs = {k: v for k, v in seed_data.INVALID_ASSOCIATION_WRONG_SCHEMA_VERSION.items() if k != "fixture_id"}
        with self.assertRaises(gate.GateValidationError):
            gate.insert_association(self.conn, **kwargs)
        after = _snapshot(self.conn)
        self.assertEqual(before, after)

    def test_full_rejection_pass_leaves_no_trace_beyond_the_valid_load(self):
        before = _snapshot(self.conn)
        ingest.attempt_rejected_fixtures(self.conn)
        after = _snapshot(self.conn)
        self.assertEqual(before, after)


class TestNamespaceIntegrityWithRealFixtures(IngestTestCase):
    """
    Re-proves B4/T15 using this milestone's actual dataset (not synthetic
    examples), end to end: the split fails before registration, succeeds
    after, using the exact fixtures load_seed_dataset() uses.
    """

    def test_split_fails_before_registry_entry_exists(self):
        for node in seed_data.NODES:
            gate.insert_node(self.conn, **node)
        gate.insert_node(self.conn, **seed_data.ENTITY_SPLIT_NEW_NODE)
        with self.assertRaises(gate.GateValidationError) as ctx:
            gate.insert_entity_lineage(self.conn, **seed_data.ENTITY_LINEAGE)
        self.assertIn("xerdna_namespace_registry", str(ctx.exception))

    def test_split_succeeds_after_registry_entry_exists(self):
        for node in seed_data.NODES:
            gate.insert_node(self.conn, **node)
        gate.insert_node(self.conn, **seed_data.ENTITY_SPLIT_NEW_NODE)
        from GRAPH.engine.ingest import _register_namespace_entries
        _register_namespace_entries(self.conn)
        lineage_id = gate.insert_entity_lineage(self.conn, **seed_data.ENTITY_LINEAGE)
        self.assertIsInstance(lineage_id, int)


class TestIngestModuleIsGateOnly(unittest.TestCase):
    """
    Structural proof that ingest.py writes exclusively through gate.py,
    with exactly one documented exception (the namespace registry, which
    gate.py has no dedicated function for).
    """

    def test_no_raw_sql_writes_outside_the_documented_exception(self):
        source = inspect.getsource(ingest)
        # split the module at the one function permitted to contain SQL
        marker = "def _register_namespace_entries"
        boundary = source.index(marker)
        rest_of_module = source[:boundary] + source[source.index("\n\n\n", boundary) + 3:]
        for keyword in ("INSERT INTO", "UPDATE ", "DELETE FROM"):
            with self.subTest(keyword=keyword):
                self.assertNotIn(keyword, rest_of_module)

    def test_only_one_sql_write_function_exists(self):
        sql_functions = [
            name for name, obj in inspect.getmembers(ingest, inspect.isfunction)
            if obj.__module__ == ingest.__name__ and "conn.execute" in inspect.getsource(obj)
        ]
        self.assertEqual(sql_functions, ["_register_namespace_entries"])


if __name__ == "__main__":
    unittest.main()
