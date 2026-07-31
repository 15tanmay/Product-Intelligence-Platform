"""AnalyticsService: thin adapter between use-cases and SQLite.

Wraps pandas.read_sql_query so every use-case module gets a consistent
interface and errors are surfaced as DatabaseError (not raw sqlite3 exceptions).

Thread safety: each call opens its own connection via get_connection(), which
returns a new sqlite3.Connection. SQLite's WAL mode allows concurrent reads.
"""
import pandas as pd

from database.db import get_connection
from app_logging.logger import get_logger

logger = get_logger(__name__)


class DatabaseError(Exception):
    """Raised when a SQL query fails or returns an unexpected result."""


class AnalyticsService:
    """Thin adapter that executes SQL and returns pandas DataFrames.

    Can be used either as a singleton or instantiated per-use-case.
    All methods are instance methods for consistency and testability.
    """

    def execute_query(
        self,
        query: str,
        params: tuple = (),
    ) -> pd.DataFrame:
        """Execute *query* with optional *params* and return a DataFrame.

        Returns an empty DataFrame on error rather than propagating exceptions
        to allow dashboards to degrade gracefully.

        Raises:
            DatabaseError: if the database connection or query execution fails.
        """
        try:
            with get_connection() as conn:
                return pd.read_sql_query(query, conn, params=params)
        except Exception as exc:
            logger.error(f"Query execution failed: {exc}")
            raise DatabaseError(
                "A database error occurred while fetching analytics data."
            ) from exc
