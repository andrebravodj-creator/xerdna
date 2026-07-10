"""
Database initialization.

Traces to:
  DOCS/PHASE_002_DESIGN.md Section 3 (Technology Choice) -- PRAGMA foreign_keys = ON
    is set on every connection this engine opens, with no code path that
    opens a connection without it.
  DOCS/PHASE_002_DESIGN.md Section 4 (Storage Structure) -- schema.sql
    implements the 9 tables described there.

This module does not implement Section 5 (The Insertion Gate) -- see
schema.sql's header comment for the exact scope boundary.
"""

import sqlite3
import sys
from pathlib import Path

from GRAPH.engine import config
from GRAPH.engine.logging_setup import get_logger

EXPECTED_TABLES = frozenset({
    "nodes",
    "node_xrefs",
    "associations",
    "confidence",
    "hypotheses",
    "predictions",
    "checked_absent",
    "entity_lineage",
    "xerdna_namespace_registry",
})


def check_python_version() -> None:
    """Raise RuntimeError if running under an unsupported Python version."""
    if sys.version_info[:2] < config.MIN_PYTHON_VERSION:
        raise RuntimeError(
            f"XERDNA engine requires Python >= "
            f"{'.'.join(map(str, config.MIN_PYTHON_VERSION))}; "
            f"running under {sys.version_info.major}.{sys.version_info.minor}."
        )


def connect(db_path: Path = config.DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Open a connection to the local SQLite database file with foreign-key
    enforcement enabled. Every connection this module opens goes through
    this function -- there is no other code path that opens a connection.
    """
    check_python_version()
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Path = config.DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Create the database file (if it doesn't exist) and apply schema.sql.
    Idempotent -- safe to call against an already-initialized database.
    Returns an open connection with foreign keys enabled.
    """
    logger = get_logger()
    conn = connect(db_path)

    schema_sql = Path(config.SCHEMA_SQL_PATH).read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()

    logger.info(
        "Database initialized at %s (engine_version=%s, schema_version=%s)",
        db_path,
        config.ENGINE_VERSION,
        config.SUPPORTED_SCHEMA_VERSION,
    )
    return conn


def list_tables(conn: sqlite3.Connection) -> set:
    """Return the set of table names present in the database."""
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table';"
    ).fetchall()
    return {row[0] for row in rows}


def foreign_keys_enabled(conn: sqlite3.Connection) -> bool:
    """Return whether PRAGMA foreign_keys is currently ON for this connection."""
    (value,) = conn.execute("PRAGMA foreign_keys;").fetchone()
    return bool(value)
