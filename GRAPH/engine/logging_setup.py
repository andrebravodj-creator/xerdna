"""
Local-only logging configuration.

Traces to: DOCS/PHASE_002_DESIGN.md Section 2 (In scope -- "no server process,
no network listener") and the "logging" deliverable of Engineering Milestone 001.

Uses only Python's standard library. Writes to a local file and to stdout --
both local, neither networked. No SMTPHandler, HTTPHandler, SysLogHandler,
or any other network-capable logging handler is used anywhere in this module.
"""

import logging
import sys
from pathlib import Path

from GRAPH.engine import config

_LOGGER_NAME = "xerdna.engine"


def configure_logging(log_path: Path = config.DEFAULT_LOG_PATH) -> logging.Logger:
    """
    Configure and return the engine's logger.

    Idempotent: calling this more than once does not duplicate handlers.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.propagate = False
    return logger


def get_logger() -> logging.Logger:
    """Return the engine's logger, configuring it with defaults if needed."""
    logger = logging.getLogger(_LOGGER_NAME)
    if not logger.handlers:
        return configure_logging()
    return logger
