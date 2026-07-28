import pandas as pd
from database.db import get_connection
from app_logging.logger import get_logger

logger = get_logger(__name__)

class DatabaseError(Exception):
    pass

class AnalyticsService:
    @staticmethod
    def execute_query(query: str, params: tuple = ()) -> pd.DataFrame:
        try:
            with get_connection() as conn:
                return pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise DatabaseError("A database error occurred while fetching analytics data.") from e
