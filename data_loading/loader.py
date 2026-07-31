"""Data loading pipeline for the Product Intelligence Platform.

Supports two strategies:
  - Incremental upsert: For tables with stable primary keys (INSERT OR REPLACE via
    temp-table staging). The target table is never dropped, preserving all data.
  - Schema-managed replace: For tables with no single PK (e.g. geolocation). The
    table is dropped and recreated from the schema DDL, so indexes are always
    reapplied. A dedicated post-load step re-applies schema indexes.
"""
import pandas as pd
import sqlite3

from database.db import get_connection, initialize_database
from config.settings import DATA_DIR, DATASET_FILES, REPLACE_ONLY_TABLES, SCHEMA_PATH
from app_logging.logger import get_logger
from validation.validator import DataValidator

logger = get_logger(__name__)


def _validate_dataframe(df: pd.DataFrame, table_name: str) -> bool:
    """Run full validation (schema, PK uniqueness, null checks) for *table_name*.

    Delegates to DataValidator.validate_table which uses the shared constants
    in config.dataset_schema for column expectations, PK definitions, and
    critical-column null thresholds.

    Returns True if the DataFrame is safe to load, False otherwise.
    """
    return DataValidator.validate_table(df, table_name)


def _reapply_indexes() -> None:
    """Re-apply all CREATE INDEX statements from schema.sql.

    Required after any full-replace load (e.g. geolocation) which drops the
    table and recreates it as a raw pandas table without the schema-defined indexes.
    """
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql = f.read()

    index_statements = [
        stmt.strip() + ";"
        for stmt in sql.split(";")
        if "CREATE INDEX" in stmt.upper()
    ]

    if not index_statements:
        return

    with get_connection() as conn:
        for stmt in index_statements:
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError as exc:
                # Already exists or table not yet present — both are safe to ignore
                logger.debug(f"Index statement skipped ({exc}): {stmt[:60]}")
        conn.commit()

    logger.info(f"Re-applied {len(index_statements)} index(es) from schema.sql.")


def load_csv_to_table(csv_name: str, table_name: str) -> int:
    """Incrementally upsert a CSV into a SQLite table using INSERT OR REPLACE.

    Uses a temp-table staging approach so the target table is never dropped,
    preserving all historical data that may have been added outside the CSV.

    Returns the number of rows processed, or -1 on failure.
    """
    csv_path = DATA_DIR / csv_name
    if not csv_path.exists():
        logger.error(f"CSV not found: {csv_path}")
        return -1

    logger.info(f"Loading '{csv_name}' into '{table_name}' (incremental upsert)...")
    df = pd.read_csv(csv_path, low_memory=False)

    if not _validate_dataframe(df, table_name):
        return -1

    temp_table = f"_tmp_{table_name}"
    with get_connection() as conn:
        df.to_sql(temp_table, conn, if_exists="replace", index=False)
        columns = ", ".join([f'"{c}"' for c in df.columns])
        upsert_sql = (
            f"INSERT OR REPLACE INTO {table_name} ({columns}) "
            f"SELECT {columns} FROM {temp_table}"
        )
        conn.execute(upsert_sql)
        conn.execute(f"DROP TABLE {temp_table}")
        conn.commit()

    logger.info(f"Processed {len(df):,} rows for '{table_name}' (incremental upsert).")
    return len(df)


def load_csv_replace(csv_name: str, table_name: str) -> int:
    """Schema-managed full replace for tables without a stable primary key.

    Drops the pandas-created table, recreates from schema DDL, then reloads data.
    Indexes are always reapplied after this operation.

    Returns the number of rows loaded, or -1 on failure.
    """
    csv_path = DATA_DIR / csv_name
    if not csv_path.exists():
        logger.error(f"CSV not found: {csv_path}")
        return -1

    logger.info(f"Loading '{csv_name}' into '{table_name}' (full replace)...")
    df = pd.read_csv(csv_path, low_memory=False)

    if not _validate_dataframe(df, table_name):
        return -1

    with get_connection() as conn:
        # Drop existing table (could be schema-managed or raw pandas table)
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()

    # Reinitialize recreates the table from DDL and all indexes
    initialize_database()

    with get_connection() as conn:
        df.to_sql(table_name, conn, if_exists="append", index=False)
        conn.commit()

    logger.info(f"Loaded {len(df):,} rows into '{table_name}' (full replace).")
    return len(df)


def verify_row_counts() -> dict[str, int]:
    """Query actual row counts for all expected tables and return a summary dict."""
    all_tables = list(DATASET_FILES.keys()) + list(REPLACE_ONLY_TABLES.keys())
    counts: dict[str, int] = {}
    with get_connection() as conn:
        for table in all_tables:
            try:
                result = conn.execute(f"SELECT COUNT(*) FROM [{table}]").fetchone()
                counts[table] = result[0] if result else 0
            except Exception as exc:
                logger.error(f"Could not count rows in '{table}': {exc}")
                counts[table] = -1
    return counts


def verify_referential_integrity() -> list[str]:
    """Check FK integrity for key relationships and return a list of violation summaries."""
    checks = [
        ("orders without matching customer",
         "SELECT COUNT(*) FROM orders o LEFT JOIN customers c ON o.customer_id = c.customer_id WHERE c.customer_id IS NULL"),
        ("order_items without matching order",
         "SELECT COUNT(*) FROM order_items oi LEFT JOIN orders o ON oi.order_id = o.order_id WHERE o.order_id IS NULL"),
        ("order_items without matching product",
         "SELECT COUNT(*) FROM order_items oi LEFT JOIN products p ON oi.product_id = p.product_id WHERE p.product_id IS NULL"),
        ("order_items without matching seller",
         "SELECT COUNT(*) FROM order_items oi LEFT JOIN sellers s ON oi.seller_id = s.seller_id WHERE s.seller_id IS NULL"),
        ("order_payments without matching order",
         "SELECT COUNT(*) FROM order_payments op LEFT JOIN orders o ON op.order_id = o.order_id WHERE o.order_id IS NULL"),
        ("reviews without matching order",
         "SELECT COUNT(*) FROM reviews r LEFT JOIN orders o ON r.order_id = o.order_id WHERE o.order_id IS NULL"),
    ]
    violations: list[str] = []
    with get_connection() as conn:
        for label, query in checks:
            try:
                count = conn.execute(query).fetchone()[0]
                status = "OK" if count == 0 else f"VIOLATION ({count:,} rows)"
                logger.info(f"FK check — {label}: {status}")
                if count > 0:
                    violations.append(f"{label}: {count:,} orphan rows")
            except Exception as exc:
                logger.error(f"FK check failed for '{label}': {exc}")
    return violations


def run_all_loads() -> None:
    """Initialize schema, load all configured datasets, verify counts and integrity."""
    initialize_database()

    row_counts: dict[str, int] = {}

    # Load FK-parent tables first (products, sellers, customers), then children
    for table, csv_name in DATASET_FILES.items():
        count = load_csv_to_table(csv_name, table)
        row_counts[table] = count

    # Full-replace tables (no stable PK)
    for table, csv_name in REPLACE_ONLY_TABLES.items():
        count = load_csv_replace(csv_name, table)
        row_counts[table] = count

    # Always reapply indexes at the end (covers geolocation and any others)
    _reapply_indexes()

    # ── Verification ─────────────────────────────────────────────────────────
    logger.info("=== ROW COUNT VERIFICATION ===")
    actual_counts = verify_row_counts()
    all_ok = True
    for table, actual in actual_counts.items():
        loaded = row_counts.get(table, 0)
        match = "OK" if actual == loaded or (table in REPLACE_ONLY_TABLES and actual > 0) else "MISMATCH"
        if match == "MISMATCH":
            all_ok = False
        logger.info(f"  {table:<45} loaded={loaded:>10,}  db={actual:>10,}  [{match}]")

    logger.info("=== REFERENTIAL INTEGRITY CHECK ===")
    violations = verify_referential_integrity()
    if violations:
        for v in violations:
            logger.warning(f"  FK violation: {v}")
    else:
        logger.info("  All FK relationships are clean.")

    if all_ok and not violations:
        logger.info("All datasets loaded and verified successfully.")
    else:
        logger.warning("Load completed with warnings — review logs above.")


if __name__ == "__main__":
    run_all_loads()
