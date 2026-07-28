import pandas as pd
from adapters.analytics_service import AnalyticsService

class CohortAnalytics:
    def __init__(self, service: AnalyticsService):
        self.service = service

    def get_monthly_cohorts(self) -> pd.DataFrame:
        query = """
        WITH first_purchase AS (
            SELECT c.customer_unique_id, MIN(strftime('%Y-%m', o.order_purchase_timestamp)) as cohort_month
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        ),
        purchases AS (
            SELECT c.customer_unique_id, strftime('%Y-%m', o.order_purchase_timestamp) as purchase_month
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
        )
        SELECT 
            fp.cohort_month,
            p.purchase_month,
            COUNT(DISTINCT p.customer_unique_id) as active_customers
        FROM first_purchase fp
        JOIN purchases p ON fp.customer_unique_id = p.customer_unique_id
        GROUP BY 1, 2
        ORDER BY 1, 2;
        """
        return self.service.execute_query(query)
