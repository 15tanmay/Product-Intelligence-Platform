import unittest
import unittest.mock
import sqlite3
import pandas as pd
from pathlib import Path
from adapters.analytics_service import AnalyticsService

class TestSQLIntegration(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        
        schema_path = Path('t:/product/database/schema.sql')
        with open(schema_path, 'r') as f:
            self.conn.executescript(f.read())
            
        self.conn.execute("INSERT INTO customers (customer_id, customer_unique_id) VALUES ('c1', 'u1')")
        self.conn.execute("INSERT INTO orders (order_id, customer_id, order_status, order_purchase_timestamp) VALUES ('o1', 'c1', 'delivered', '2023-01-01 10:00:00')")
        self.conn.execute("INSERT INTO order_items (order_id, order_item_id, product_id, price, freight_value) VALUES ('o1', 1, 'p1', 100.0, 10.0)")
        self.conn.commit()

        self.patcher = unittest.mock.patch('adapters.analytics_service.get_connection')
        self.mock_get_conn = self.patcher.start()
        self.mock_get_conn.return_value = self.conn

    def tearDown(self):
        self.patcher.stop()
        self.conn.close()

    def test_revenue_query(self):
        query = """
        SELECT 
            strftime('%Y-%m', o.order_purchase_timestamp) AS month,
            SUM(oi.price + oi.freight_value) as total_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY 1
        """
        df = AnalyticsService.execute_query(query)
        
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['month'], '2023-01')
        self.assertEqual(df.iloc[0]['total_revenue'], 110.0)
