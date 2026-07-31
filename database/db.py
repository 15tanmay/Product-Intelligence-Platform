"""SQLite connection and schema initialisation helpers.

Design decisions:
  - WAL mode is enabled for better read/write concurrency.
  - Foreign key enforcement is enabled per-connection.
  - Row factory is set to sqlite3.Row for dict-like access by column name.
  - Returns a plain Connection; callers use it as a context manager for
    transaction control (conn.commit() / conn.rollback()).
"""
import sqlite3
from contextlib import contextmanager
from typing import Generator

from config.settings import DB_PATH, SCHEMA_PATH
from app_logging.logger import get_logger

logger = get_logger(__name__)


def get_connection(timeout: float = 30.0) -> sqlite3.Connection:
    """Open a SQLite connection with WAL mode, FK enforcement, and busy timeout.

    Args:
        timeout: Seconds to wait when the database is locked by another writer.
                 Default 30 s is sufficient for concurrent Streamlit + loader usage.
    """
    conn = sqlite3.connect(DB_PATH, timeout=timeout)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=30000;")  # 30 000 ms = 30 s
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def managed_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager that opens a connection, yields it, and always closes it.

    Use this for batch operations that must guarantee the connection is closed
    even if an exception is raised.

    Example::

        with managed_connection() as conn:
            conn.execute("INSERT INTO ...")
            conn.commit()
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def initialize_database() -> None:
    """Create all tables and indexes defined in schema.sql (idempotent)."""
    logger.info("Initializing database...")
    if not SCHEMA_PATH.exists():
        logger.error(f"Schema not found: {SCHEMA_PATH}")
        return

    with get_connection() as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

    logger.info("Database initialized successfully.")
