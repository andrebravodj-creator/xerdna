"""
Engine configuration constants.

Traces to:
  DOCS/PHASE_002_DESIGN.md Section 9 (Versioning)  -- ENGINE_VERSION, SUPPORTED_SCHEMA_VERSION
  DOCS/PHASE_002_DESIGN.md Section 3 (Technology Choice) -- MIN_PYTHON_VERSION, paths

No record whose schema_version does not equal SUPPORTED_SCHEMA_VERSION is
accepted by the (future) insertion gate -- this prototype does not attempt
multi-version compatibility (Section 9).
"""

from pathlib import Path

# --- Versioning (Section 9) ---
ENGINE_VERSION = "0.1.0"
SUPPORTED_SCHEMA_VERSION = "1.2"

# --- Runtime requirement (Section 3, WVS4) ---
MIN_PYTHON_VERSION = (3, 10)

# --- Paths ---
_ENGINE_DIR = Path(__file__).resolve().parent
DATA_DIR = _ENGINE_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "xerdna_engine.db"
DEFAULT_LOG_PATH = DATA_DIR / "engine.log"
SCHEMA_SQL_PATH = _ENGINE_DIR / "schema.sql"
