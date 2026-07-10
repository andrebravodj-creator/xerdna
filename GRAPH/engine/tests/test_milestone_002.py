"""
Validation framework for Engineering Milestone 002 -- The Insertion Gate.

Traces to: DOCS/PHASE_002_DESIGN.md Section 5 (The Insertion Gate), Section 8
(Test Matrix). Built incrementally, one task at a time, mirroring
GRAPH/engine/gate.py's own construction; test classes are grouped by the
task that introduced the code they validate.

Standard library only (unittest), consistent with Milestone 001.
"""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from GRAPH.engine import config, db, gate


class GateTestCase(unittest.TestCase):
    """Common fixture: a freshly-initialized, temporary database per test."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test_engine.db"
        self.conn = db.init_db(self.db_path)

    def tearDown(self):
        self.conn.close()
        self._tmpdir.cleanup()


# --- Task 1: gate foundation (validators, allow-list config) ---

class TestUniversalValidators(unittest.TestCase):
    def test_valid_universal_fields_pass(self):
        gate._validate_universal(
            schema_version=config.SUPPORTED_SCHEMA_VERSION,
            evidence_tier="established_evidence",
            primary_knowledge_source="infores:hgnc",
            source_record_id="HGNC:1100",
            status="active",
        )  # must not raise

    def test_wrong_schema_version_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate._validate_universal(
                schema_version="9.9",
                evidence_tier="established_evidence",
                primary_knowledge_source="infores:hgnc",
                source_record_id="HGNC:1100",
                status="active",
            )

    def test_invalid_tier_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate._validate_universal(
                schema_version=config.SUPPORTED_SCHEMA_VERSION,
                evidence_tier="not_a_real_tier",
                primary_knowledge_source="infores:hgnc",
                source_record_id="HGNC:1100",
                status="active",
            )

    def test_empty_primary_knowledge_source_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate._validate_universal(
                schema_version=config.SUPPORTED_SCHEMA_VERSION,
                evidence_tier="established_evidence",
                primary_knowledge_source="",
                source_record_id="HGNC:1100",
                status="active",
            )

    def test_invalid_status_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate._validate_universal(
                schema_version=config.SUPPORTED_SCHEMA_VERSION,
                evidence_tier="established_evidence",
                primary_knowledge_source="infores:hgnc",
                source_record_id="HGNC:1100",
                status="not_a_real_status",
            )

    def test_superseded_by_status_accepted_at_universal_layer(self):
        gate._validate_universal(
            schema_version=config.SUPPORTED_SCHEMA_VERSION,
            evidence_tier="established_evidence",
            primary_knowledge_source="infores:hgnc",
            source_record_id="HGNC:1100",
            status="superseded_by:xerdna:gene:999",
        )  # format is valid here; referential check is separate (see below)


class TestSupersededByValidation(GateTestCase):
    def test_superseded_by_existing_node_accepted(self):
        self.conn.execute(
            """
            INSERT INTO nodes (xerdna_id, category, evidence_tier, primary_knowledge_source,
                                retrieved_at, source_record_id, schema_version)
            VALUES ('xerdna:gene:001', 'biolink:Gene', 'established_evidence', 'infores:hgnc',
                    '2026-07-10', 'HGNC:1100', ?)
            """,
            (config.SUPPORTED_SCHEMA_VERSION,),
        )
        gate._validate_superseded_by(self.conn, "nodes", "xerdna_id", "superseded_by:xerdna:gene:001")

    def test_superseded_by_nonexistent_node_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate._validate_superseded_by(self.conn, "nodes", "xerdna_id", "superseded_by:xerdna:gene:does_not_exist")

    def test_active_status_skips_check(self):
        gate._validate_superseded_by(self.conn, "nodes", "xerdna_id", "active")  # must not raise


class TestNamespaceRegistryCheck(GateTestCase):
    def test_non_xerdna_term_skips_check(self):
        gate._check_namespace_registered(self.conn, "biolink:Gene", "entity_type")  # must not raise

    def test_unregistered_xerdna_term_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate._check_namespace_registered(self.conn, "xerdna:split_into", "predicate")

    def test_registered_active_xerdna_term_accepted(self):
        self.conn.execute(
            """
            INSERT INTO xerdna_namespace_registry (prefix, kind, introduced_in, rationale)
            VALUES ('split_into', 'predicate', 'DOCS/PHASE_002_DESIGN.md', 'R2 split/merge lineage')
            """
        )
        gate._check_namespace_registered(self.conn, "xerdna:split_into", "predicate")  # must not raise

    def test_deprecated_xerdna_term_rejected(self):
        self.conn.execute(
            """
            INSERT INTO xerdna_namespace_registry (prefix, kind, introduced_in, rationale, status)
            VALUES ('old_predicate', 'predicate', 'DOCS/PHASE_002_DESIGN.md', 'test fixture', 'deprecated')
            """
        )
        with self.assertRaises(gate.GateValidationError):
            gate._check_namespace_registered(self.conn, "xerdna:old_predicate", "predicate")


# --- Task 2: immutability triggers (Section 5.3 point 2) ---

class TestImmutabilityTriggers(GateTestCase):
    def _insert_node(self, xerdna_id="xerdna:gene:001"):
        self.conn.execute(
            """
            INSERT INTO nodes (xerdna_id, category, evidence_tier, primary_knowledge_source,
                                retrieved_at, source_record_id, schema_version)
            VALUES (?, 'biolink:Gene', 'established_evidence', 'infores:hgnc',
                    '2026-07-10', 'HGNC:1100', ?)
            """,
            (xerdna_id, config.SUPPORTED_SCHEMA_VERSION),
        )
        self.conn.commit()

    def _insert_association(self):
        self._insert_node("xerdna:gene:001")
        self._insert_node("xerdna:gene:002")
        cur = self.conn.execute(
            """
            INSERT INTO associations (subject_id, object_id, predicate, evidence_tier,
                                       primary_knowledge_source, source_record_id, retrieved_at, schema_version)
            VALUES ('xerdna:gene:001', 'xerdna:gene:002', 'biolink:interacts_with', 'established_evidence',
                    'infores:hgnc', 'HGNC:1100', '2026-07-10', ?)
            """,
            (config.SUPPORTED_SCHEMA_VERSION,),
        )
        self.conn.commit()
        return cur.lastrowid

    def test_node_evidence_tier_update_rejected(self):
        self._insert_node()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "UPDATE nodes SET evidence_tier = 'computational_prediction' WHERE xerdna_id = 'xerdna:gene:001'"
            )

    def test_node_schema_version_update_rejected(self):
        self._insert_node()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("UPDATE nodes SET schema_version = '9.9' WHERE xerdna_id = 'xerdna:gene:001'")

    def test_node_xerdna_id_update_rejected(self):
        self._insert_node()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "UPDATE nodes SET xerdna_id = 'xerdna:gene:renamed' WHERE xerdna_id = 'xerdna:gene:001'"
            )

    def test_node_other_field_update_still_allowed(self):
        self._insert_node()
        self.conn.execute("UPDATE nodes SET status = 'retracted' WHERE xerdna_id = 'xerdna:gene:001'")
        self.conn.commit()
        (status,) = self.conn.execute(
            "SELECT status FROM nodes WHERE xerdna_id = 'xerdna:gene:001'"
        ).fetchone()
        self.assertEqual(status, "retracted")

    def test_association_evidence_tier_update_rejected(self):
        assoc_id = self._insert_association()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "UPDATE associations SET evidence_tier = 'computational_prediction' WHERE id = ?", (assoc_id,)
            )

    def test_association_schema_version_update_rejected(self):
        assoc_id = self._insert_association()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("UPDATE associations SET schema_version = '9.9' WHERE id = ?", (assoc_id,))

    def test_association_id_update_rejected(self):
        assoc_id = self._insert_association()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("UPDATE associations SET id = ? WHERE id = ?", (assoc_id + 1000, assoc_id))


# --- Task 3: insert_node() ---

class TestInsertNode(GateTestCase):
    def test_valid_node_with_xrefs_succeeds(self):
        gate.insert_node(
            self.conn,
            xerdna_id="xerdna:gene:001",
            category="biolink:Gene",
            evidence_tier="established_evidence",
            primary_knowledge_source="infores:hgnc",
            source_record_id="HGNC:1100",
            retrieved_at="2026-07-10",
            xrefs=[("HGNC", "1100"), ("NCBIGene", "672")],
        )
        row = self.conn.execute(
            "SELECT xerdna_id FROM nodes WHERE xerdna_id = 'xerdna:gene:001'"
        ).fetchone()
        self.assertIsNotNone(row)
        xref_count = self.conn.execute(
            "SELECT COUNT(*) FROM node_xrefs WHERE xerdna_id = 'xerdna:gene:001'"
        ).fetchone()[0]
        self.assertEqual(xref_count, 2)

    def test_valid_node_with_no_xref_rationale_succeeds(self):
        # xerdna:Patent must be registered first (B4) -- registering it here
        # is incidental to this test, whose actual subject is the
        # no_xref_rationale mechanism (Rule 1), not the registry check
        # (already covered by TestNamespaceRegistryCheck).
        self.conn.execute(
            """
            INSERT INTO xerdna_namespace_registry (prefix, kind, parent_type, introduced_in, rationale)
            VALUES ('Patent', 'entity_type', 'biolink:InformationContentEntity',
                    'DOCS/PHASE_002_DESIGN.md', 'GRAPH/SCHEMA.md Biological Entity Types')
            """
        )
        gate.insert_node(
            self.conn,
            xerdna_id="xerdna:patent:001",
            category="xerdna:Patent",
            evidence_tier="established_evidence",
            primary_knowledge_source="infores:uspto",
            source_record_id="US1234567",
            retrieved_at="2026-07-10",
            no_xref_rationale="Patent minted directly from filing; no external xref database applies.",
        )
        row = self.conn.execute(
            "SELECT no_xref_rationale FROM nodes WHERE xerdna_id = 'xerdna:patent:001'"
        ).fetchone()
        self.assertIsNotNone(row[0])

    def test_no_xrefs_and_no_rationale_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_node(
                self.conn,
                xerdna_id="xerdna:gene:002",
                category="biolink:Gene",
                evidence_tier="established_evidence",
                primary_knowledge_source="infores:hgnc",
                source_record_id="HGNC:1101",
                retrieved_at="2026-07-10",
            )
        # nothing written
        row = self.conn.execute(
            "SELECT 1 FROM nodes WHERE xerdna_id = 'xerdna:gene:002'"
        ).fetchone()
        self.assertIsNone(row)

    def test_invalid_evidence_tier_rejected_before_write(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_node(
                self.conn,
                xerdna_id="xerdna:gene:003",
                category="biolink:Gene",
                evidence_tier="bogus",
                primary_knowledge_source="infores:hgnc",
                source_record_id="HGNC:1102",
                retrieved_at="2026-07-10",
                xrefs=[("HGNC", "1102")],
            )

    def test_unregistered_xerdna_category_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_node(
                self.conn,
                xerdna_id="xerdna:widget:001",
                category="xerdna:Widget",
                evidence_tier="established_evidence",
                primary_knowledge_source="infores:hgnc",
                source_record_id="W1",
                retrieved_at="2026-07-10",
                no_xref_rationale="test",
            )


# --- Task 4: insert_association() core (established_evidence, E2) ---

class AssociationTestCase(GateTestCase):
    def setUp(self):
        super().setUp()
        gate.insert_node(
            self.conn, xerdna_id="xerdna:gene:001", category="biolink:Gene",
            evidence_tier="established_evidence", primary_knowledge_source="infores:hgnc",
            source_record_id="HGNC:1100", retrieved_at="2026-07-10", xrefs=[("HGNC", "1100")],
        )
        gate.insert_node(
            self.conn, xerdna_id="xerdna:disease:001", category="biolink:Disease",
            evidence_tier="established_evidence", primary_knowledge_source="infores:hgnc",
            source_record_id="MONDO:0000001", retrieved_at="2026-07-10", xrefs=[("MONDO", "0000001")],
        )


class TestInsertAssociationEstablishedEvidence(AssociationTestCase):
    def test_valid_correlated_with_succeeds(self):
        assoc_id = gate.insert_association(
            self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:correlated_with", evidence_tier="established_evidence",
            primary_knowledge_source="infores:hgnc", source_record_id="STUDY:1",
            retrieved_at="2026-07-10",
        )
        self.assertIsInstance(assoc_id, int)

    def test_causes_without_source_span_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_association(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:causes", evidence_tier="established_evidence",
                primary_knowledge_source="infores:hgnc", source_record_id="STUDY:2",
                retrieved_at="2026-07-10",
            )

    def test_causes_with_source_span_succeeds(self):
        assoc_id = gate.insert_association(
            self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:causes", evidence_tier="established_evidence",
            primary_knowledge_source="infores:hgnc", source_record_id="STUDY:3",
            retrieved_at="2026-07-10",
            source_span="Study Section 4.2: 'variant X was shown to directly cause condition Y in vivo.'",
        )
        self.assertIsInstance(assoc_id, int)

    def test_source_not_on_allowlist_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_association(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:correlated_with", evidence_tier="established_evidence",
                primary_knowledge_source="infores:not_on_the_allowlist", source_record_id="STUDY:4",
                retrieved_at="2026-07-10",
            )

    def test_established_evidence_with_confidence_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_association(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:correlated_with", evidence_tier="established_evidence",
                primary_knowledge_source="infores:hgnc", source_record_id="STUDY:5",
                retrieved_at="2026-07-10", confidence_type="numeric", confidence_value="0.9",
            )
        # nothing written -- rollback confirmed
        count = self.conn.execute("SELECT COUNT(*) FROM associations").fetchone()[0]
        self.assertEqual(count, 0)


# --- Task 5: computational_prediction support ---

class TestInsertAssociationPrediction(AssociationTestCase):
    def test_valid_prediction_succeeds(self):
        assoc_id = gate.insert_association(
            self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:correlated_with", evidence_tier="computational_prediction",
            primary_knowledge_source="infores:xerdna-model", source_record_id="RUN:1",
            retrieved_at="2026-07-10",
            prediction_method="gradient-boosted-association-model",
            prediction_model_version="0.1.0",
            prediction_input_reference="xerdna:gene:001, xerdna:disease:001",
            prediction_generated_at="2026-07-10",
            confidence_type="numeric", confidence_value="0.72",
        )
        method_ontology_gap = self.conn.execute(
            "SELECT ontology_gap FROM predictions WHERE association_id = ?", (assoc_id,)
        ).fetchone()[0]
        self.assertEqual(method_ontology_gap, 1)  # no method_ontology_term supplied -> gap flagged

    def test_prediction_missing_method_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_association(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:correlated_with", evidence_tier="computational_prediction",
                primary_knowledge_source="infores:xerdna-model", source_record_id="RUN:2",
                retrieved_at="2026-07-10",
                prediction_model_version="0.1.0", prediction_input_reference="x",
                prediction_generated_at="2026-07-10", confidence_type="numeric",
            )

    def test_prediction_missing_confidence_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_association(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:correlated_with", evidence_tier="computational_prediction",
                primary_knowledge_source="infores:xerdna-model", source_record_id="RUN:3",
                retrieved_at="2026-07-10",
                prediction_method="m", prediction_model_version="0.1.0",
                prediction_input_reference="x", prediction_generated_at="2026-07-10",
            )

    def test_prediction_with_ontology_term_no_gap(self):
        assoc_id = gate.insert_association(
            self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:correlated_with", evidence_tier="computational_prediction",
            primary_knowledge_source="infores:xerdna-model", source_record_id="RUN:4",
            retrieved_at="2026-07-10",
            prediction_method="m", prediction_method_ontology_term="OBI:0000001",
            prediction_model_version="0.1.0", prediction_input_reference="x",
            prediction_generated_at="2026-07-10", confidence_type="qualitative",
            confidence_basis="model produces no natural numeric score",
        )
        gap = self.conn.execute(
            "SELECT ontology_gap FROM predictions WHERE association_id = ?", (assoc_id,)
        ).fetchone()[0]
        self.assertEqual(gap, 0)


# --- Task 6: insert_hypothesis() ---

class TestInsertHypothesis(AssociationTestCase):
    def setUp(self):
        super().setUp()
        gate.insert_node(
            self.conn, xerdna_id="xerdna:protein:001", category="biolink:Protein",
            evidence_tier="established_evidence", primary_knowledge_source="infores:uniprot",
            source_record_id="P12345", retrieved_at="2026-07-10", xrefs=[("UniProt", "P12345")],
        )

    def test_valid_hypothesis_succeeds(self):
        assoc_id = gate.insert_hypothesis(
            self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:gene_associated_with_condition",
            primary_knowledge_source="infores:xerdna-reasoning", source_record_id="HYP:1",
            retrieved_at="2026-07-10",
            claim="Gene X, via Protein Y, may modulate Disease Z",
            supporting_evidence="xerdna:gene:001 correlated_with xerdna:disease:001",
            reasoning="Co-occurrence of the gene-disease correlation and a known protein interaction "
                      "suggests a plausible mechanistic path worth investigating.",
            generated_by="xerdna-reasoning-engine-stub",
            confidence_basis="two independent structural signals point the same direction",
            none_found_as_of="2026-07-10",
        )
        row = self.conn.execute(
            "SELECT status FROM hypotheses WHERE association_id = ?", (assoc_id,)
        ).fetchone()
        self.assertEqual(row[0], "open")
        tier = self.conn.execute(
            "SELECT evidence_tier FROM associations WHERE id = ?", (assoc_id,)
        ).fetchone()[0]
        self.assertEqual(tier, "research_hypothesis")

    def test_missing_claim_rejected_nothing_written(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_hypothesis(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:gene_associated_with_condition",
                primary_knowledge_source="infores:xerdna-reasoning", source_record_id="HYP:2",
                retrieved_at="2026-07-10", claim="",
                supporting_evidence="x", reasoning="x", generated_by="x",
                confidence_basis="x", none_found_as_of="2026-07-10",
            )
        count = self.conn.execute("SELECT COUNT(*) FROM associations").fetchone()[0]
        self.assertEqual(count, 0)

    def test_missing_contradicting_and_none_found_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_hypothesis(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:gene_associated_with_condition",
                primary_knowledge_source="infores:xerdna-reasoning", source_record_id="HYP:3",
                retrieved_at="2026-07-10", claim="a claim",
                supporting_evidence="x", reasoning="x", generated_by="x", confidence_basis="x",
            )

    def test_commit_false_composition_rolls_back_atomically(self):
        """
        White-box test of the _commit=False composition pattern
        insert_hypothesis() relies on: if a step after
        insert_association(_commit=False) fails, the association row must
        not be left behind as an orphan -- the whole thing is one
        transaction, not two.
        """
        association_id = gate.insert_association(
            self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:gene_associated_with_condition", evidence_tier="research_hypothesis",
            primary_knowledge_source="infores:xerdna-reasoning", source_record_id="HYP:5",
            retrieved_at="2026-07-10", confidence_type="qualitative", confidence_basis="x",
            _commit=False,
        )
        with self.assertRaises(sqlite3.IntegrityError):
            # hypotheses.claim is NOT NULL -- inserted directly to bypass
            # insert_hypothesis()'s own Python-level check and force a
            # failure strictly after the association insert has already run.
            self.conn.execute(
                "INSERT INTO hypotheses (association_id, claim, supporting_evidence, "
                "none_found_as_of, reasoning, generated_by) VALUES (?, NULL, 'x', '2026-07-10', 'x', 'x')",
                (association_id,),
            )
        self.conn.rollback()
        count = self.conn.execute(
            "SELECT COUNT(*) FROM associations WHERE id = ?", (association_id,)
        ).fetchone()[0]
        self.assertEqual(count, 0, "rollback must undo the uncommitted association insert too")


# --- Task 7: promote_prediction() ---

class TestPromotePrediction(AssociationTestCase):
    def test_promotion_end_to_end(self):
        prediction_id = gate.insert_association(
            self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:correlated_with", evidence_tier="computational_prediction",
            primary_knowledge_source="infores:xerdna-model", source_record_id="RUN:1",
            retrieved_at="2026-07-10",
            prediction_method="m", prediction_model_version="0.1.0",
            prediction_input_reference="x", prediction_generated_at="2026-07-10",
            confidence_type="numeric", confidence_value="0.8",
        )
        established_id = gate.promote_prediction(
            self.conn, prediction_association_id=prediction_id,
            subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:correlated_with",
            primary_knowledge_source="infores:hgnc", source_record_id="STUDY:CONFIRM:1",
            retrieved_at="2026-07-11",
        )
        # both independently queryable
        original_tier = self.conn.execute(
            "SELECT evidence_tier FROM associations WHERE id = ?", (prediction_id,)
        ).fetchone()[0]
        self.assertEqual(original_tier, "computational_prediction")
        new_tier, promoted_from = self.conn.execute(
            "SELECT evidence_tier, promoted_from FROM associations WHERE id = ?", (established_id,)
        ).fetchone()
        self.assertEqual(new_tier, "established_evidence")
        self.assertEqual(promoted_from, prediction_id)

    def test_promotion_from_nonexistent_prediction_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.promote_prediction(
                self.conn, prediction_association_id=999999,
                subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:correlated_with",
                primary_knowledge_source="infores:hgnc", source_record_id="STUDY:2",
                retrieved_at="2026-07-11",
            )

    def test_promotion_from_established_evidence_rejected(self):
        already_established_id = gate.insert_association(
            self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:correlated_with", evidence_tier="established_evidence",
            primary_knowledge_source="infores:hgnc", source_record_id="STUDY:3",
            retrieved_at="2026-07-10",
        )
        with self.assertRaises(gate.GateValidationError):
            gate.promote_prediction(
                self.conn, prediction_association_id=already_established_id,
                subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:correlated_with",
                primary_knowledge_source="infores:hgnc", source_record_id="STUDY:4",
                retrieved_at="2026-07-11",
            )

    def test_promotion_from_hypothesis_rejected(self):
        gate.insert_node(
            self.conn, xerdna_id="xerdna:protein:002", category="biolink:Protein",
            evidence_tier="established_evidence", primary_knowledge_source="infores:uniprot",
            source_record_id="P99999", retrieved_at="2026-07-10", xrefs=[("UniProt", "P99999")],
        )
        hyp_id = gate.insert_hypothesis(
            self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:gene_associated_with_condition",
            primary_knowledge_source="infores:xerdna-reasoning", source_record_id="HYP:1",
            retrieved_at="2026-07-10", claim="a claim", supporting_evidence="x",
            reasoning="x", generated_by="x", confidence_basis="x", none_found_as_of="2026-07-10",
        )
        with self.assertRaises(gate.GateValidationError):
            gate.promote_prediction(
                self.conn, prediction_association_id=hyp_id,
                subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:correlated_with",
                primary_knowledge_source="infores:hgnc", source_record_id="STUDY:5",
                retrieved_at="2026-07-11",
            )


# --- Task 8: resolve_hypothesis() (T18) ---

class TestResolveHypothesis(AssociationTestCase):
    def setUp(self):
        super().setUp()
        self.hyp_id = gate.insert_hypothesis(
            self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:gene_associated_with_condition",
            primary_knowledge_source="infores:xerdna-reasoning", source_record_id="HYP:1",
            retrieved_at="2026-07-10", claim="a claim", supporting_evidence="x",
            reasoning="x", generated_by="x", confidence_basis="x", none_found_as_of="2026-07-10",
        )

    def test_resolution_end_to_end(self):
        resolving_id = gate.resolve_hypothesis(
            self.conn, hypothesis_association_id=self.hyp_id, new_status="supported_by_experiment",
            subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:gene_associated_with_condition",
            primary_knowledge_source="infores:hgnc", source_record_id="EXPERIMENT:1",
            retrieved_at="2026-07-11",
        )
        status, resolved_by = self.conn.execute(
            "SELECT status, resolved_by FROM hypotheses WHERE association_id = ?", (self.hyp_id,)
        ).fetchone()
        self.assertEqual(status, "supported_by_experiment")
        self.assertEqual(resolved_by, resolving_id)
        resolving_tier = self.conn.execute(
            "SELECT evidence_tier FROM associations WHERE id = ?", (resolving_id,)
        ).fetchone()[0]
        self.assertEqual(resolving_tier, "established_evidence")
        # original hypothesis association untouched
        original_tier = self.conn.execute(
            "SELECT evidence_tier FROM associations WHERE id = ?", (self.hyp_id,)
        ).fetchone()[0]
        self.assertEqual(original_tier, "research_hypothesis")

    def test_resolution_with_resolved_by_empty_before_resolution(self):
        resolved_by_before = self.conn.execute(
            "SELECT resolved_by FROM hypotheses WHERE association_id = ?", (self.hyp_id,)
        ).fetchone()[0]
        self.assertIsNone(resolved_by_before)

    def test_resolution_to_invalid_status_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.resolve_hypothesis(
                self.conn, hypothesis_association_id=self.hyp_id, new_status="open",
                subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:gene_associated_with_condition",
                primary_knowledge_source="infores:hgnc", source_record_id="EXPERIMENT:2",
                retrieved_at="2026-07-11",
            )

    def test_resolution_of_nonexistent_hypothesis_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.resolve_hypothesis(
                self.conn, hypothesis_association_id=999999, new_status="refuted",
                subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:gene_associated_with_condition",
                primary_knowledge_source="infores:hgnc", source_record_id="EXPERIMENT:3",
                retrieved_at="2026-07-11",
            )

    def test_resolution_of_non_hypothesis_tier_rejected(self):
        established_id = gate.insert_association(
            self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:correlated_with", evidence_tier="established_evidence",
            primary_knowledge_source="infores:hgnc", source_record_id="STUDY:X",
            retrieved_at="2026-07-10",
        )
        with self.assertRaises(gate.GateValidationError):
            gate.resolve_hypothesis(
                self.conn, hypothesis_association_id=established_id, new_status="refuted",
                subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:gene_associated_with_condition",
                primary_knowledge_source="infores:hgnc", source_record_id="EXPERIMENT:4",
                retrieved_at="2026-07-11",
            )


# --- Task 9: insert_checked_absent(), insert_entity_lineage() (T5, T15, T16) ---

class TestInsertCheckedAbsent(GateTestCase):
    def test_valid_checked_absent_succeeds(self):
        record_id = gate.insert_checked_absent(
            self.conn, subject="xerdna:gene:001", predicate="biolink:correlated_with",
            object="xerdna:disease:001", checked_by="manual seed", checked_at="2026-07-10",
            scope="hand-authored seed only",
        )
        self.assertIsInstance(record_id, int)

    def test_checked_absent_has_no_evidence_tier_requirement(self):
        # no evidence_tier kwarg exists on the function signature at all --
        # this is a structural assertion the function cannot even accept one
        import inspect
        params = inspect.signature(gate.insert_checked_absent).parameters
        self.assertNotIn("evidence_tier", params)

    def test_missing_scope_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_checked_absent(
                self.conn, subject="xerdna:gene:001", predicate="biolink:correlated_with",
                object="xerdna:disease:001", checked_by="manual seed", checked_at="2026-07-10",
                scope="",
            )


class TestInsertEntityLineage(GateTestCase):
    def setUp(self):
        super().setUp()
        gate.insert_node(
            self.conn, xerdna_id="xerdna:gene:001-old", category="biolink:Gene",
            evidence_tier="established_evidence", primary_knowledge_source="infores:hgnc",
            source_record_id="HGNC:1100", retrieved_at="2026-07-10", xrefs=[("HGNC", "1100")],
        )
        gate.insert_node(
            self.conn, xerdna_id="xerdna:gene:001-new", category="biolink:Gene",
            evidence_tier="established_evidence", primary_knowledge_source="infores:hgnc",
            source_record_id="HGNC:1100-rev2", retrieved_at="2026-07-10", xrefs=[("HGNC", "1100")],
        )

    def test_split_without_registry_entry_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_entity_lineage(
                self.conn, old_xerdna_id="xerdna:gene:001-old", new_xerdna_id="xerdna:gene:001-new",
                relation="split_into", recorded_at="2026-07-10",
            )

    def test_split_with_registry_entry_succeeds(self):
        self.conn.execute(
            """
            INSERT INTO xerdna_namespace_registry (prefix, kind, introduced_in, rationale)
            VALUES ('split_into', 'predicate', 'DOCS/PHASE_002_DESIGN.md', 'R2 split/merge lineage')
            """
        )
        record_id = gate.insert_entity_lineage(
            self.conn, old_xerdna_id="xerdna:gene:001-old", new_xerdna_id="xerdna:gene:001-new",
            relation="split_into", recorded_at="2026-07-10",
        )
        self.assertIsInstance(record_id, int)
        # old node's row is not deleted
        old_row = self.conn.execute(
            "SELECT 1 FROM nodes WHERE xerdna_id = 'xerdna:gene:001-old'"
        ).fetchone()
        self.assertIsNotNone(old_row)

    def test_invalid_relation_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_entity_lineage(
                self.conn, old_xerdna_id="xerdna:gene:001-old", new_xerdna_id="xerdna:gene:001-new",
                relation="not_a_real_relation", recorded_at="2026-07-10",
            )


# --- Task 10: explicit Design Section 8 Test Matrix (T1-T18) coverage check ---
#
# Most T-numbers are already exercised, sometimes multiple times, by the
# task-level test classes above. This class closes the remaining gaps and
# makes the T-number <-> test correspondence explicit and complete, rather
# than leaving it implicit in scattered tests. T14 (read-path guarantee) is
# NOT implemented this milestone -- no read/query layer was built (Section 2
# scope boundary, restated in this milestone's own kickoff) -- and is
# recorded here as consciously deferred, not silently skipped.

class TestDesignMatrixRemainingCoverage(AssociationTestCase):
    def test_T1_missing_evidence_tier_rejected(self):
        # evidence_tier has no default in either function -- Python itself
        # refuses the call before the gate's own logic even runs.
        with self.assertRaises(TypeError):
            gate.insert_association(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:correlated_with",
                primary_knowledge_source="infores:hgnc", source_record_id="X",
                retrieved_at="2026-07-10",
            )

    def test_T3_missing_source_record_id_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_association(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:correlated_with", evidence_tier="established_evidence",
                primary_knowledge_source="infores:hgnc", source_record_id="",
                retrieved_at="2026-07-10",
            )

    def test_T4_wrong_schema_version_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_association(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:correlated_with", evidence_tier="established_evidence",
                primary_knowledge_source="infores:hgnc", source_record_id="X",
                retrieved_at="2026-07-10", schema_version="0.9",
            )

    def test_T11_missing_reasoning_rejected(self):
        with self.assertRaises(gate.GateValidationError):
            gate.insert_hypothesis(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:gene_associated_with_condition",
                primary_knowledge_source="infores:xerdna-reasoning", source_record_id="HYP:X",
                retrieved_at="2026-07-10", claim="a claim", supporting_evidence="x",
                reasoning="", generated_by="x", confidence_basis="x", none_found_as_of="2026-07-10",
            )

    def test_T13_resolution_status_defaults_not_checked_never_settable(self):
        import inspect
        # the gate exposes no way to set resolution_status at all -- Rule 4's
        # honest-deferral guarantee holds structurally, not by runtime check
        self.assertNotIn("resolution_status", inspect.signature(gate.insert_association).parameters)
        assoc_id = gate.insert_association(
            self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
            predicate="biolink:correlated_with", evidence_tier="established_evidence",
            primary_knowledge_source="infores:hgnc", source_record_id="X",
            retrieved_at="2026-07-10",
        )
        (resolution_status,) = self.conn.execute(
            "SELECT resolution_status FROM associations WHERE id = ?", (assoc_id,)
        ).fetchone()
        self.assertEqual(resolution_status, "not_checked")

    def test_T14_read_path_not_implemented_this_milestone(self):
        self.assertFalse(
            hasattr(__import__("GRAPH.engine.gate", fromlist=["gate"]), "query"),
            "no read/query layer exists yet -- Section 2's WVS2 canonical query layer "
            "is out of scope for Milestone 002 (Insertion Gate) by design",
        )

    def test_T16_split_preserves_both_ids_fully(self):
        gate.insert_node(
            self.conn, xerdna_id="xerdna:gene:005-old", category="biolink:Gene",
            evidence_tier="established_evidence", primary_knowledge_source="infores:hgnc",
            source_record_id="HGNC:5", retrieved_at="2026-07-10", xrefs=[("HGNC", "5")],
        )
        gate.insert_node(
            self.conn, xerdna_id="xerdna:gene:005-new", category="biolink:Gene",
            evidence_tier="established_evidence", primary_knowledge_source="infores:hgnc",
            source_record_id="HGNC:5-rev", retrieved_at="2026-07-10", xrefs=[("HGNC", "5")],
        )
        self.conn.execute(
            """
            INSERT INTO xerdna_namespace_registry (prefix, kind, introduced_in, rationale)
            VALUES ('split_into', 'predicate', 'DOCS/PHASE_002_DESIGN.md', 'R2')
            """
        )
        gate.insert_entity_lineage(
            self.conn, old_xerdna_id="xerdna:gene:005-old", new_xerdna_id="xerdna:gene:005-new",
            relation="split_into", recorded_at="2026-07-10",
        )
        old_id, new_id = self.conn.execute(
            "SELECT old_xerdna_id, new_xerdna_id FROM entity_lineage WHERE old_xerdna_id = 'xerdna:gene:005-old'"
        ).fetchone()
        self.assertEqual(old_id, "xerdna:gene:005-old")
        self.assertEqual(new_id, "xerdna:gene:005-new")
        # both node rows still present -- neither deleted by the lineage insert
        both_present = self.conn.execute(
            "SELECT COUNT(*) FROM nodes WHERE xerdna_id IN ('xerdna:gene:005-old', 'xerdna:gene:005-new')"
        ).fetchone()[0]
        self.assertEqual(both_present, 2)


# --- G3 fix (DOCS/MILESTONE_002_REVIEW.md): every public entry point must
# --- verify PRAGMA foreign_keys = ON and fail immediately, descriptively,
# --- if it is not.

class TestForeignKeysEnforcementCheck(GateTestCase):
    """
    Each test uses a connection that is otherwise correctly initialized
    (schema applied) but has foreign_keys explicitly turned OFF -- isolating
    "foreign keys disabled" as the only variable under test, distinct from
    "table doesn't exist" or any other setup problem.
    """

    def setUp(self):
        super().setUp()
        self.conn.execute("PRAGMA foreign_keys = OFF;")
        self.assertFalse(db.foreign_keys_enabled(self.conn))  # sanity check on the fixture itself

    def test_insert_node_fails_fast_and_descriptively(self):
        with self.assertRaises(gate.GateValidationError) as ctx:
            gate.insert_node(
                self.conn, xerdna_id="xerdna:gene:001", category="biolink:Gene",
                evidence_tier="established_evidence", primary_knowledge_source="infores:hgnc",
                source_record_id="HGNC:1100", retrieved_at="2026-07-10",
                no_xref_rationale="test",
            )
        self.assertIn("foreign_keys", str(ctx.exception))
        # nothing written
        self.assertIsNone(self.conn.execute("SELECT 1 FROM nodes").fetchone())

    def test_insert_association_fails_fast(self):
        with self.assertRaises(gate.GateValidationError) as ctx:
            gate.insert_association(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:correlated_with", evidence_tier="established_evidence",
                primary_knowledge_source="infores:hgnc", source_record_id="X", retrieved_at="2026-07-10",
            )
        self.assertIn("foreign_keys", str(ctx.exception))

    def test_insert_hypothesis_fails_fast(self):
        with self.assertRaises(gate.GateValidationError) as ctx:
            gate.insert_hypothesis(
                self.conn, subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:gene_associated_with_condition",
                primary_knowledge_source="infores:xerdna-reasoning", source_record_id="HYP:1",
                retrieved_at="2026-07-10", claim="x", supporting_evidence="x",
                reasoning="x", generated_by="x", confidence_basis="x", none_found_as_of="2026-07-10",
            )
        self.assertIn("foreign_keys", str(ctx.exception))

    def test_promote_prediction_fails_fast(self):
        with self.assertRaises(gate.GateValidationError) as ctx:
            gate.promote_prediction(
                self.conn, prediction_association_id=1,
                subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:correlated_with",
                primary_knowledge_source="infores:hgnc", source_record_id="X", retrieved_at="2026-07-10",
            )
        self.assertIn("foreign_keys", str(ctx.exception))

    def test_resolve_hypothesis_fails_fast(self):
        with self.assertRaises(gate.GateValidationError) as ctx:
            gate.resolve_hypothesis(
                self.conn, hypothesis_association_id=1, new_status="refuted",
                subject_id="xerdna:gene:001", object_id="xerdna:disease:001",
                predicate="biolink:gene_associated_with_condition",
                primary_knowledge_source="infores:hgnc", source_record_id="X", retrieved_at="2026-07-10",
            )
        self.assertIn("foreign_keys", str(ctx.exception))

    def test_insert_checked_absent_fails_fast(self):
        with self.assertRaises(gate.GateValidationError) as ctx:
            gate.insert_checked_absent(
                self.conn, subject="xerdna:gene:001", predicate="biolink:correlated_with",
                object="xerdna:disease:001", checked_by="manual seed", checked_at="2026-07-10",
                scope="test",
            )
        self.assertIn("foreign_keys", str(ctx.exception))
        self.assertIsNone(self.conn.execute("SELECT 1 FROM checked_absent").fetchone())

    def test_insert_entity_lineage_fails_fast(self):
        with self.assertRaises(gate.GateValidationError) as ctx:
            gate.insert_entity_lineage(
                self.conn, old_xerdna_id="xerdna:gene:001-old", new_xerdna_id="xerdna:gene:001-new",
                relation="split_into", recorded_at="2026-07-10",
            )
        self.assertIn("foreign_keys", str(ctx.exception))
        self.assertIsNone(self.conn.execute("SELECT 1 FROM entity_lineage").fetchone())

    def test_all_public_entry_points_are_covered(self):
        """
        Structural guarantee that this test class doesn't silently fall out
        of sync with gate.py's public API -- every insert_*/promote_*/
        resolve_*/add_* function must appear as a check above.

        Updated in Milestone 005: gate.add_xref() was added as an 8th
        public entry point (not 7); its own foreign-keys-enabled check is
        covered by GRAPH/engine/tests/test_milestone_005.py's
        test_add_xref_requires_foreign_keys_enabled, not duplicated here.
        This test's job is only to confirm the *set* of public entry
        points matches what this file already accounts for.
        """
        import inspect
        public_entry_points = {
            name for name, obj in inspect.getmembers(gate, inspect.isfunction)
            if not name.startswith("_") and obj.__module__ == gate.__name__
        }
        expected = {
            "insert_node", "insert_association", "insert_hypothesis",
            "promote_prediction", "resolve_hypothesis",
            "insert_checked_absent", "insert_entity_lineage",
            "add_xref",
        }
        self.assertEqual(public_entry_points, expected)


class TestForeignKeysEnforcementCheckPositive(GateTestCase):
    """Confirms the check does NOT interfere with normal, correctly-configured use."""

    def test_normal_connection_passes_the_check_and_inserts_succeed(self):
        self.assertTrue(db.foreign_keys_enabled(self.conn))  # db.init_db() sets this by default
        gate.insert_node(
            self.conn, xerdna_id="xerdna:gene:001", category="biolink:Gene",
            evidence_tier="established_evidence", primary_knowledge_source="infores:hgnc",
            source_record_id="HGNC:1100", retrieved_at="2026-07-10", xrefs=[("HGNC", "1100")],
        )
        row = self.conn.execute("SELECT 1 FROM nodes WHERE xerdna_id = 'xerdna:gene:001'").fetchone()
        self.assertIsNotNone(row)


if __name__ == "__main__":
    unittest.main()
