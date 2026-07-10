"""
Validation framework for Engineering Milestone 005 -- Entity Identity and
Xref Resolution.

Traces to: GRAPH/SCHEMA.md's Entity Identity section ("resolves to the
existing canonical node and appends the xref -- it does not create a
duplicate... Unresolvable ambiguity... is itself recorded as a
research_hypothesis-tier relationship... rather than silently merged or
silently dropped"); Anti-Hallucination Rule 5 (no silent fuzzy merging).

Uses only GRAPH/engine/sources/fixtures/hgnc_sample.json (Milestone 004's
real, committed HGNC fixture) plus one small, clearly-labeled synthetic
record for exercising ambiguity. Fully offline -- no network access
anywhere in this file or the modules it exercises.

Standard library only (unittest).
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from GRAPH.engine import config, db, gate, identity
from GRAPH.engine.sources import hgnc_mapper

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "sources" / "fixtures" / "hgnc_sample.json"


class IdentityTestCase(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test_engine.db"
        self.conn = db.init_db(self.db_path)

    def tearDown(self):
        self.conn.close()
        self._tmpdir.cleanup()


def _real_kwargs(symbol: str) -> dict:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    doc = next(d for d in fixture["docs"] if d["symbol"] == symbol)
    return hgnc_mapper.map_hgnc_record_to_node_kwargs(doc, fixture["fetched_at"])


# --- Task 1: gate.add_xref() ---

class TestAddXref(IdentityTestCase):
    def setUp(self):
        super().setUp()
        gate.insert_node(self.conn, **_real_kwargs("BRCA1"))

    def test_append_new_xref_succeeds(self):
        gate.add_xref(self.conn, xerdna_id="xerdna:gene:hgnc-1100", namespace="OMIM", external_id="113705")
        count = self.conn.execute(
            "SELECT COUNT(*) FROM node_xrefs WHERE xerdna_id = 'xerdna:gene:hgnc-1100' AND namespace = 'OMIM'"
        ).fetchone()[0]
        self.assertEqual(count, 1)

    def test_append_to_nonexistent_node_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.add_xref(self.conn, xerdna_id="xerdna:gene:does-not-exist", namespace="OMIM", external_id="1")

    def test_exact_duplicate_triple_is_idempotent_noop(self):
        gate.add_xref(self.conn, xerdna_id="xerdna:gene:hgnc-1100", namespace="HGNC", external_id="1100")
        count = self.conn.execute(
            "SELECT COUNT(*) FROM node_xrefs WHERE xerdna_id = 'xerdna:gene:hgnc-1100' AND namespace = 'HGNC'"
        ).fetchone()[0]
        self.assertEqual(count, 1)  # still just one row -- already existed from insert_node()

    def test_conflation_across_different_nodes_rejected(self):
        gate.insert_node(self.conn, **_real_kwargs("TP53"))
        with self.assertRaises(gate.GateValidationError) as ctx:
            # HGNC:1100 already belongs to BRCA1's node -- attaching it to TP53's node would conflate them
            gate.add_xref(self.conn, xerdna_id="xerdna:gene:hgnc-11998", namespace="HGNC", external_id="1100")
        self.assertIn("conflate", str(ctx.exception))

    def test_add_xref_requires_foreign_keys_enabled(self):
        self.conn.execute("PRAGMA foreign_keys = OFF;")
        with self.assertRaises(gate.GateValidationError) as ctx:
            gate.add_xref(self.conn, xerdna_id="xerdna:gene:hgnc-1100", namespace="OMIM", external_id="113705")
        self.assertIn("foreign_keys", str(ctx.exception))


# --- Tasks 2-3: identity resolution core + ambiguity recording ---

class TestResolveOrCreateNode(IdentityTestCase):
    def test_first_ingestion_creates(self):
        resolution = identity.resolve_or_create_node(self.conn, _real_kwargs("BRCA1"))
        self.assertEqual(resolution.outcome, "created")
        self.assertEqual(resolution.xerdna_id, "xerdna:gene:hgnc-1100")
        count = self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        self.assertEqual(count, 1)

    def test_same_record_again_resolves_not_duplicates(self):
        identity.resolve_or_create_node(self.conn, _real_kwargs("BRCA1"))
        resolution = identity.resolve_or_create_node(self.conn, _real_kwargs("BRCA1"))
        self.assertEqual(resolution.outcome, "resolved_existing")
        self.assertEqual(resolution.xerdna_id, "xerdna:gene:hgnc-1100")
        self.assertEqual(resolution.xrefs_appended, [])  # already all present -- nothing new
        count = self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        self.assertEqual(count, 1)  # still exactly one node

    def test_different_candidate_id_same_xref_resolves_to_original(self):
        """A record proposing a DIFFERENT xerdna_id, but sharing a real xref, must not create a second node."""
        identity.resolve_or_create_node(self.conn, _real_kwargs("BRCA1"))
        kwargs = dict(_real_kwargs("BRCA1"))
        kwargs["xerdna_id"] = "xerdna:gene:some-other-minting-scheme"  # deliberately different candidate ID
        resolution = identity.resolve_or_create_node(self.conn, kwargs)
        self.assertEqual(resolution.outcome, "resolved_existing")
        self.assertEqual(resolution.xerdna_id, "xerdna:gene:hgnc-1100")  # original canonical ID wins, not the new candidate
        count = self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        self.assertEqual(count, 1)
        no_such_node = self.conn.execute(
            "SELECT 1 FROM nodes WHERE xerdna_id = 'xerdna:gene:some-other-minting-scheme'"
        ).fetchone()
        self.assertIsNone(no_such_node)

    def test_new_partial_overlap_appends_missing_xrefs_only(self):
        identity.resolve_or_create_node(self.conn, _real_kwargs("BRCA1"))
        kwargs = dict(_real_kwargs("BRCA1"))
        kwargs["xerdna_id"] = "xerdna:gene:alt-id"
        kwargs["xrefs"] = [*kwargs["xrefs"], ("OMIM", "113705")]  # one genuinely new xref
        resolution = identity.resolve_or_create_node(self.conn, kwargs)
        self.assertEqual(resolution.outcome, "resolved_existing")
        self.assertEqual(resolution.xrefs_appended, [("OMIM", "113705")])
        count = self.conn.execute(
            "SELECT COUNT(*) FROM node_xrefs WHERE xerdna_id = 'xerdna:gene:hgnc-1100' AND namespace = 'OMIM'"
        ).fetchone()[0]
        self.assertEqual(count, 1)

    def test_ambiguous_record_rejected_not_merged(self):
        identity.resolve_or_create_node(self.conn, _real_kwargs("BRCA1"))
        identity.resolve_or_create_node(self.conn, _real_kwargs("TP53"))
        # synthetic, clearly-labeled test record combining BRCA1's real HGNC xref
        # with TP53's real NCBIGene xref -- deliberately spans two existing nodes
        ambiguous_kwargs = {
            "xerdna_id": "xerdna:gene:synthetic-ambiguous-test-record",
            "category": "biolink:Gene",
            "evidence_tier": "established_evidence",
            "primary_knowledge_source": "infores:hgnc",
            "source_record_id": "SYNTHETIC:AMBIGUOUS:1",
            "retrieved_at": "2026-07-11",
            "schema_version": config.SUPPORTED_SCHEMA_VERSION,
            "xrefs": [("HGNC", "1100"), ("NCBIGene", "7157")],  # BRCA1's HGNC id + TP53's Entrez id
        }
        with self.assertRaises(identity.AmbiguousIdentityError) as ctx:
            identity.resolve_or_create_node(self.conn, ambiguous_kwargs)
        self.assertEqual(ctx.exception.matched_xerdna_ids, frozenset({"xerdna:gene:hgnc-1100", "xerdna:gene:hgnc-11998"}))
        # nothing written: no third node, no xref conflation, no merge
        count = self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        self.assertEqual(count, 2)  # still just BRCA1 and TP53's nodes
        no_synthetic_node = self.conn.execute(
            "SELECT 1 FROM nodes WHERE xerdna_id = 'xerdna:gene:synthetic-ambiguous-test-record'"
        ).fetchone()
        self.assertIsNone(no_synthetic_node)

    def test_requires_non_empty_xrefs(self):
        kwargs = dict(_real_kwargs("BRCA1"))
        kwargs["xrefs"] = []
        with self.assertRaises(ValueError):
            identity.resolve_or_create_node(self.conn, kwargs)


class TestRecordPossiblySameAs(IdentityTestCase):
    def test_records_ambiguity_as_qualitative_hypothesis(self):
        identity.resolve_or_create_node(self.conn, _real_kwargs("BRCA1"))
        identity.resolve_or_create_node(self.conn, _real_kwargs("TP53"))
        hyp_id = identity.record_possibly_same_as(
            self.conn, xerdna_id_a="xerdna:gene:hgnc-1100", xerdna_id_b="xerdna:gene:hgnc-11998",
            reason="synthetic test record's xrefs spanned both nodes",
        )
        predicate, tier = self.conn.execute(
            "SELECT predicate, evidence_tier FROM associations WHERE id = ?", (hyp_id,)
        ).fetchone()
        self.assertEqual(predicate, "xerdna:possibly_same_as")
        self.assertEqual(tier, "research_hypothesis")

    def test_ambiguous_rejection_does_not_automatically_record_a_hypothesis(self):
        identity.resolve_or_create_node(self.conn, _real_kwargs("BRCA1"))
        identity.resolve_or_create_node(self.conn, _real_kwargs("TP53"))
        ambiguous_kwargs = {
            "xerdna_id": "xerdna:gene:synthetic-2",
            "category": "biolink:Gene", "evidence_tier": "established_evidence",
            "primary_knowledge_source": "infores:hgnc", "source_record_id": "SYNTHETIC:2",
            "retrieved_at": "2026-07-11", "schema_version": config.SUPPORTED_SCHEMA_VERSION,
            "xrefs": [("HGNC", "1100"), ("NCBIGene", "7157")],
        }
        with self.assertRaises(identity.AmbiguousIdentityError):
            identity.resolve_or_create_node(self.conn, ambiguous_kwargs)
        count = self.conn.execute(
            "SELECT COUNT(*) FROM associations WHERE predicate = 'xerdna:possibly_same_as'"
        ).fetchone()[0]
        self.assertEqual(count, 0)  # rejection alone never records anything -- a separate, explicit call is required


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


def _load_full_fixture(conn) -> list:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    resolutions = []
    for doc in fixture["docs"]:
        kwargs = hgnc_mapper.map_hgnc_record_to_node_kwargs(doc, fixture["fetched_at"])
        resolutions.append(identity.resolve_or_create_node(conn, kwargs))
    return resolutions


class TestIdempotentFullFixtureReingestion(IdentityTestCase):
    def test_first_pass_creates_all_three(self):
        resolutions = _load_full_fixture(self.conn)
        self.assertTrue(all(r.outcome == "created" for r in resolutions))
        count = self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        self.assertEqual(count, 3)

    def test_second_pass_is_a_true_noop(self):
        _load_full_fixture(self.conn)
        before = _snapshot(self.conn)
        resolutions = _load_full_fixture(self.conn)
        after = _snapshot(self.conn)
        self.assertEqual(before, after)  # byte-for-byte identical -- genuinely idempotent
        self.assertTrue(all(r.outcome == "resolved_existing" for r in resolutions))
        self.assertTrue(all(r.xrefs_appended == [] for r in resolutions))

    def test_ten_repeated_passes_stay_at_three_nodes(self):
        for _ in range(10):
            _load_full_fixture(self.conn)
        count = self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        self.assertEqual(count, 3)


class TestSplitMergeLineageUnaffected(IdentityTestCase):
    """R2 (GRAPH/SCHEMA.md) is unchanged by this milestone -- gate.insert_entity_lineage() still works standalone,
    and identity resolution does not interfere with or duplicate its job."""

    def test_entity_lineage_still_works_via_gate_directly(self):
        identity.resolve_or_create_node(self.conn, _real_kwargs("BRCA1"))
        gate.insert_node(
            self.conn, xerdna_id="xerdna:gene:hgnc-1100-b", category="biolink:Gene",
            evidence_tier="established_evidence", primary_knowledge_source="infores:hgnc",
            source_record_id="HGNC:1100-rev2", retrieved_at="2026-07-11",
            xrefs=[("HGNC", "1100-rev2")],
        )
        self.conn.execute(
            """
            INSERT INTO xerdna_namespace_registry (prefix, kind, introduced_in, rationale)
            VALUES ('split_into', 'predicate', 'DOCS/PHASE_002_DESIGN.md', 'R2')
            """
        )
        self.conn.commit()
        lineage_id = gate.insert_entity_lineage(
            self.conn, old_xerdna_id="xerdna:gene:hgnc-1100", new_xerdna_id="xerdna:gene:hgnc-1100-b",
            relation="split_into", recorded_at="2026-07-11",
        )
        self.assertIsInstance(lineage_id, int)
        # old node's row is not deleted -- same guarantee as before this milestone
        old_row = self.conn.execute("SELECT 1 FROM nodes WHERE xerdna_id = 'xerdna:gene:hgnc-1100'").fetchone()
        self.assertIsNotNone(old_row)

    def test_identity_resolution_never_calls_insert_entity_lineage(self):
        import inspect
        source = inspect.getsource(identity)
        self.assertNotIn("insert_entity_lineage", source)


class TestAtomicRollbackMilestone005(IdentityTestCase):
    def test_conflation_rejection_leaves_no_trace(self):
        identity.resolve_or_create_node(self.conn, _real_kwargs("BRCA1"))
        identity.resolve_or_create_node(self.conn, _real_kwargs("TP53"))
        before = _snapshot(self.conn)
        with self.assertRaises(gate.GateValidationError):
            gate.add_xref(self.conn, xerdna_id="xerdna:gene:hgnc-11998", namespace="HGNC", external_id="1100")
        after = _snapshot(self.conn)
        self.assertEqual(before, after)

    def test_ambiguous_resolution_leaves_no_trace(self):
        identity.resolve_or_create_node(self.conn, _real_kwargs("BRCA1"))
        identity.resolve_or_create_node(self.conn, _real_kwargs("TP53"))
        before = _snapshot(self.conn)
        ambiguous_kwargs = {
            "xerdna_id": "xerdna:gene:synthetic-3", "category": "biolink:Gene",
            "evidence_tier": "established_evidence", "primary_knowledge_source": "infores:hgnc",
            "source_record_id": "SYNTHETIC:3", "retrieved_at": "2026-07-11",
            "schema_version": config.SUPPORTED_SCHEMA_VERSION,
            "xrefs": [("HGNC", "1100"), ("NCBIGene", "7157")],
        }
        with self.assertRaises(identity.AmbiguousIdentityError):
            identity.resolve_or_create_node(self.conn, ambiguous_kwargs)
        after = _snapshot(self.conn)
        self.assertEqual(before, after)


class TestOfflineCoverage(unittest.TestCase):
    def test_identity_module_has_no_networking_imports(self):
        import inspect
        source_lines = [
            line.strip() for line in inspect.getsource(identity).splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        for forbidden in ("urllib", "requests", "socket", "http.client", "hgnc_fetch"):
            with self.subTest(forbidden=forbidden):
                self.assertFalse(any(forbidden in line for line in source_lines))


if __name__ == "__main__":
    unittest.main()
