import pandas as pd
from app_logging.logger import get_logger
from config.dataset_schema import EXPECTED_COLUMNS, PRIMARY_KEYS, CRITICAL_COLUMNS

logger = get_logger(__name__)


# ── Null-ratio thresholds per column ─────────────────────────────────────────
# Columns not listed use the default threshold passed to check_nulls().
NULL_THRESHOLDS: dict[str, float] = {
    # Core identifiers must never be null
    "customer_id": 0.0,
    "customer_unique_id": 0.0,
    "order_id": 0.0,
    "product_id": 0.0,
    "seller_id": 0.0,
    "review_id": 0.0,
    # Operational columns — some nulls are expected (e.g. undelivered orders)
    "order_delivered_customer_date": 0.5,
    "order_delivered_carrier_date": 0.5,
    "order_approved_at": 0.05,
    # Financial columns
    "price": 0.0,
    "freight_value": 0.0,
    "payment_value": 0.0,
    # Review columns — comments are often absent
    "review_comment_title": 1.0,
    "review_comment_message": 1.0,
    "review_score": 0.02,
}


class DataValidator:
    """Stateless validation utilities for Olist dataset DataFrames."""

    @staticmethod
    def validate_schema(df: pd.DataFrame, required_columns: list[str]) -> bool:
        """Return True if all required columns are present in df."""
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            logger.error(f"Missing required columns: {missing}")
            return False
        return True

    @staticmethod
    def check_nulls(
        df: pd.DataFrame,
        column: str,
        threshold: float = 0.1,
    ) -> bool:
        """Return False (with a warning) if null ratio for column exceeds threshold.

        Uses NULL_THRESHOLDS for known columns; falls back to the supplied threshold.
        """
        effective_threshold = NULL_THRESHOLDS.get(column, threshold)
        null_ratio = df[column].isnull().mean()
        if null_ratio > effective_threshold:
            logger.warning(
                f"Column '{column}' null ratio {null_ratio:.2%} "
                f"exceeds threshold {effective_threshold:.2%}"
            )
            return False
        return True

    @staticmethod
    def check_primary_key_uniqueness(df: pd.DataFrame, pk_columns: list[str]) -> bool:
        """Return True if the pk_columns combination is unique across df."""
        duplicates = df.duplicated(subset=pk_columns).sum()
        if duplicates > 0:
            logger.warning(
                f"Primary key {pk_columns} has {duplicates:,} duplicate row(s)."
            )
            return False
        return True

    @staticmethod
    def validate_table(df: pd.DataFrame, table_name: str) -> bool:
        """Run all applicable validation rules for the given table.

        Returns True only if all checks pass.
        """
        required = EXPECTED_COLUMNS.get(table_name, [])
        if not DataValidator.validate_schema(df, required):
            return False

        pk_cols = PRIMARY_KEYS.get(table_name)
        if pk_cols:
            DataValidator.check_primary_key_uniqueness(df, pk_cols)

        for col in CRITICAL_COLUMNS.get(table_name, []):
            if col in df.columns:
                DataValidator.check_nulls(df, col)

        logger.info(f"Validation passed for '{table_name}' ({len(df):,} rows).")
        return True
