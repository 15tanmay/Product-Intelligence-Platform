"""Data preprocessing utilities for the Product Intelligence Platform.

Preprocessing is applied *after* raw CSV data is loaded into SQLite and *before*
it is returned by the analytics use-case layer (i.e. on DataFrames produced by
AnalyticsService.execute_query).

Design principle: preprocessing functions are pure (no side-effects) and
stateless — they take a DataFrame and return a cleaned DataFrame.  They do NOT
filter rows that analytics queries may legitimately need (e.g. non-delivered
orders are kept for funnel analysis but delivery-latency queries add their own
WHERE clause).
"""
import pandas as pd
from app_logging.logger import get_logger

logger = get_logger(__name__)

_DATETIME_COLS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "shipping_limit_date",
    "review_creation_date",
    "review_answer_timestamp",
]


class DataPreprocessor:
    """Stateless preprocessing utilities for Olist DataFrames."""

    @staticmethod
    def parse_datetimes(df: pd.DataFrame) -> pd.DataFrame:
        """Parse any known datetime columns that are present in *df*.

        Columns not present in df are silently skipped.  Invalid values are
        coerced to NaT rather than raising an exception.
        """
        for col in _DATETIME_COLS:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    @staticmethod
    def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
        """Parse datetime columns for an orders DataFrame.

        NOTE: This method no longer filters to 'delivered' status — individual
        SQL queries specify their own status filter.  Filtering here would
        silently remove data needed for funnel analysis pages.
        """
        logger.info("Cleaning orders data...")
        return DataPreprocessor.parse_datetimes(df)

    @staticmethod
    def handle_missing(
        df: pd.DataFrame,
        subset: list[str],
        strategy: str = "drop",
    ) -> pd.DataFrame:
        """Handle missing values in *subset* columns.

        Args:
            df:       Input DataFrame.
            subset:   Columns to check for missing values.
            strategy: 'drop' (default) removes rows with any nulls in subset.
                      Future strategies (e.g. 'fill') can be added here.
        """
        before = len(df)
        if strategy == "drop":
            df = df.dropna(subset=subset)
        logger.info(
            f"handle_missing({subset}, strategy={strategy!r}): "
            f"{before:,} → {len(df):,} rows ({before - len(df):,} removed)."
        )
        return df

    @staticmethod
    def coerce_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """Coerce *columns* to numeric, turning invalid entries to NaN."""
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
