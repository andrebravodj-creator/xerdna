"""
Validation framework for Engineering Milestone 001.

Traces to: DOCS/PHASE_002_DESIGN.md Section 4 (Storage Structure), Section 3
(Technology Choice), Section 9 (Versioning). Per IMPLEMENTATION_POLICY.md
Section 6, this proves Milestone 001's own deliverables -- project
structure, configuration, logging, schema creation, and database
initialization -- actually work, rather than merely asserting they do.

This suite does NOT test Section 5 (The Insertion Gate) -- that logic does
not exist yet (see schema.sql's header comment). It tests only what SQLite's
own column-level constraints enforce unassisted.

Standard library only -- no test framework dependency (unittest, not pytest),
consistent with the design's "no other runtime dependency" choice extended
to the whole project, not just the engine's own runtime.
"""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from GRAPH.engine import config, db
from GRAPH.engine.logging_setup import configure_logging


class TestProjectStructure(unittest.TestCase):
    def test_engine_package_importable(self):
        import GRAPH.engine  # noqa: F401

    def test_expected_files_exist(self):
        engine_dir = Path(config.SCHEMA_SQL_PATH).parent
        for name in ("__init__.py", "config.py", "db.py", "logging_setup.py", "schema.sql"):
            with self.subTest(file=name):
                self.assertTrue((engine_dir / name).exists())


class TestConfiguration(unittest.TestCase):
    def test_engine_version(self):
        self.assertEqual(config.ENGINE_VERSION, "0.1.0")

    def test_supported_schema_version(self):
        self.assertEqual(config.SUPPORTED_SCHEMA_VERSION, "1.2")

    def test_min_python_version(self):
        self.assertEqual(config.MIN_PYTHON_VERSION, (3, 10))


class TestLogging(unittest.TestCase):
    def test_writes_to_local_file_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "test_engine.log"
            logger = configure_logging(log_path=log_path)
            for handler in logger.handlers:
                handler.close()
            logger.handlers.clear()  # reset for a clean, isolated test
            logger = configure_logging(log_path=log_path)

            logger.info("milestone 001 validation log line")
            for handler in logger.handlers:
                handler.flush()

            self.assertTrue(log_path.exists())
            content = log_path.read_text(encoding="utf-8")
            self.assertIn("milestone 001 validation log line", content)

    def test_no_network_handlers(self):
        logger = configure_logging()
        network_handler_names = {"SMTPHandler", "HTTPHandler", "SysLogHandler", "SocketHandler"}
        for handler in logger.handlers:
            self.assertNotIn(type(handler).__name__, network_handler_names)


class TestDatabaseInitialization(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test_engine.db"

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_init_db_creates_file(self):
        conn = db.init_db(self.db_path)
        conn.close()
        self.assertTrue(self.db_path.exists())

    def test_all_nine_tables_present(self):
        conn = db.init_db(self.db_path)
        tables = db.list_tables(conn)
        conn.close()
        self.assertEqual(db.EXPECTED_TABLES, tables & db.EXPECTED_TABLES)
        self.assertEqual(len(db.EXPECTED_TABLES), 9)

    def test_foreign_keys_enabled(self):
        conn = db.init_db(self.db_path)
        enabled = db.foreign_keys_enabled(conn)
        conn.close()
        self.assertTrue(enabled)

    def test_init_db_is_idempotent(self):
        conn1 = db.init_db(self.db_path)
        conn1.close()
        conn2 = db.init_db(self.db_path)  # must not raise
        conn2.close()


class TestSingleRowConstraints(unittest.TestCase):
    """
    Proves the CHECK/NOT NULL constraints in schema.sql are actually
    enforced by SQLite itself -- independent of any future application-layer
    gate (Section 5), which does not exist yet.
    """

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test_engine.db"
        self.conn = db.init_db(self.db_path)

    def tearDown(self):
        self.conn.close()
        self._tmpdir.cleanup()

    def _insert_valid_node(self, xerdna_id="xerdna:gene:001", evidence_tier="established_evidence"):
        self.conn.execute(
            """
            INSERT INTO nodes (
                xerdna_id, category, evidence_tier, primary_knowledge_source,
                retrieved_at, source_record_id, schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (xerdna_id, "biolink:Gene", evidence_tier, "infores:hgnc",
             "2026-07-10", "HGNC:1100", config.SUPPORTED_SCHEMA_VERSION),
        )
        self.conn.commit()

    def test_valid_node_insert_succeeds(self):
        self._insert_valid_node()
        row = self.conn.execute(
            "SELECT xerdna_id FROM nodes WHERE xerdna_id = ?", ("xerdna:gene:001",)
        ).fetchone()
        self.assertIsNotNone(row)

    def test_invalid_evidence_tier_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self._insert_valid_node(evidence_tier="not_a_real_tier")

    def test_missing_required_field_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                """
                INSERT INTO nodes (
                    xerdna_id, category, evidence_tier, primary_knowledge_source,
                    retrieved_at, source_record_id, schema_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("xerdna:gene:002", "biolink:Gene", "established_evidence", None,
                 "2026-07-10", "HGNC:1101", config.SUPPORTED_SCHEMA_VERSION),
            )

    def test_invalid_status_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                """
                INSERT INTO nodes (
                    xerdna_id, category, evidence_tier, primary_knowledge_source,
                    retrieved_at, source_record_id, schema_version, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                ("xerdna:gene:003", "biolink:Gene", "established_evidence", "infores:hgnc",
                 "2026-07-10", "HGNC:1102", config.SUPPORTED_SCHEMA_VERSION, "not_a_real_status"),
            )

    def test_checked_absent_has_no_evidence_tier_column(self):
        columns = {row[1] for row in self.conn.execute("PRAGMA table_info(checked_absent);")}
        self.assertNotIn("evidence_tier", columns)

    def test_checked_absent_valid_insert_succeeds(self):
        self.conn.execute(
            """
            INSERT INTO checked_absent (subject, predicate, object, checked_by, checked_at, scope)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("xerdna:gene:001", "biolink:correlated_with", "xerdna:disease:001",
             "manual seed", "2026-07-10", "hand-authored seed only"),
        )
        self.conn.commit()
        count = self.conn.execute("SELECT COUNT(*) FROM checked_absent;").fetchone()[0]
        self.assertEqual(count, 1)

    def test_foreign_key_violation_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                """
                INSERT INTO node_xrefs (xerdna_id, namespace, external_id)
                VALUES (?, ?, ?)
                """,
                ("xerdna:gene:does_not_exist", "HGNC", "1100"),
            )
            self.conn.commit()


if __name__ == "__main__":
    unittest.main()
