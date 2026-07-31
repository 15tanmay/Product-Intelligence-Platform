"""SQL integration tests using an in-memory SQLite database.

Each test creates a fresh in-memory database populated from schema.sql,
inserts minimal fixture data, patches get_connection to return the in-memory
connection, and then calls AnalyticsService.execute_query directly.
"""
import sqlite3
import unittest
import unittest.mock
from pathlib import Path

import pandas as pd

from adapters.analytics_service import AnalyticsService


_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "database" / "schema.sql"


class TestSQLIntegration(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        with open(_SCHEMA_PATH, "r", encoding="utf-8") as fh:
            self.conn.executescript(fh.read())

        # Minimal fixture data
        self.conn.execute(
            "INSERT INTO customers (customer_id, customer_unique_id) VALUES ('c1', 'u1')"
        )
        self.conn.execute(
            "INSERT INTO orders (order_id, customer_id, order_status, "
            "order_purchase_timestamp) VALUES ('o1', 'c1', 'delivered', '2023-01-01 10:00:00')"
        )
        self.conn.execute(
            "INSERT INTO order_items (order_id, order_item_id, product_id, "
            "price, freight_value) VALUES ('o1', 1, 'p1', 100.0, 10.0)"
        )
        self.conn.commit()

        # Patch get_connection to return the in-memory connection
        self.patcher = unittest.mock.patch(
            "adapters.analytics_service.get_connection",
            return_value=self.conn,
        )
        self.patcher.start()
        self.service = AnalyticsService()

    def tearDown(self) -> None:
        self.patcher.stop()
        self.conn.close()

    # ── Revenue query ─────────────────────────────────────────────────────────
    def test_revenue_query(self) -> None:
        """Monthly revenue rolls up price + freight correctly."""
        query = """
        SELECT
            strftime('%Y-%m', o.order_purchase_timestamp) AS month,
            SUM(oi.price + oi.freight_value)               AS total_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY 1
        """
        df = self.service.execute_query(query)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["month"], "2023-01")
        self.assertAlmostEqual(df.iloc[0]["total_revenue"], 110.0)

    # ── Customer count query ──────────────────────────────────────────────────
    def test_customer_count(self) -> None:
        """Unique customer count matches fixture data."""
        df = self.service.execute_query(
            "SELECT COUNT(DISTINCT customer_unique_id) AS n FROM customers"
        )
        self.assertEqual(df.iloc[0]["n"], 1)

    # ── FK join ───────────────────────────────────────────────────────────────
    def test_order_customer_join(self) -> None:
        """Orders join to customers via customer_id."""
        df = self.service.execute_query(
            "SELECT c.customer_unique_id, o.order_id "
            "FROM orders o JOIN customers c ON o.customer_id = c.customer_id"
        )
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["customer_unique_id"], "u1")

    # ── Schema completeness ───────────────────────────────────────────────────
    def test_all_nine_tables_exist(self) -> None:
        """All 9 Olist tables must exist in the schema."""
        expected = {
            "customers", "orders", "order_items", "order_payments",
            "reviews", "products", "sellers", "geolocation",
            "product_category_name_translation",
        }
        rows = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        actual = {r[0] for r in rows}
        self.assertTrue(expected.issubset(actual), f"Missing tables: {expected - actual}")


if __name__ == "__main__":
    unittest.main()
