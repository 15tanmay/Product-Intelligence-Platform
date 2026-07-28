import pandas as pd
from adapters.analytics_service import AnalyticsService

class CustomerAnalytics:
    def __init__(self, service: AnalyticsService):
        self.service = service

    def get_first_vs_repeat_ratio(self) -> pd.DataFrame:
        query = """
        WITH customer_orders AS (
            SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) as total_orders
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        )
        SELECT 
            CASE WHEN total_orders = 1 THEN 'One-Time' ELSE 'Repeat' END as customer_type,
            COUNT(customer_unique_id) as count
        FROM customer_orders
        GROUP BY 1;
        """
        return self.service.execute_query(query)
