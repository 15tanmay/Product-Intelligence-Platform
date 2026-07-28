import pandas as pd
from adapters.analytics_service import AnalyticsService


class ExecutiveKPIs:
    """High-level executive metrics answering: why are first-time customers not returning?"""

    def __init__(self, service: AnalyticsService) -> None:
        self.service = service

    def get_high_level_metrics(self) -> dict:
        """Single-row summary of core business health indicators."""
        query = """
        SELECT
            COUNT(DISTINCT c.customer_unique_id)                         AS total_customers,
            COUNT(DISTINCT o.order_id)                                   AS total_orders,
            ROUND(SUM(oi.price + oi.freight_value), 2)                  AS total_revenue,
            ROUND(AVG(r.review_score), 2)                               AS avg_satisfaction,
            ROUND(AVG(op.payment_value), 2)                             AS avg_order_value
        FROM orders o
        JOIN customers c    ON o.customer_id  = c.customer_id
        JOIN order_items oi ON o.order_id     = oi.order_id
        LEFT JOIN reviews r ON o.order_id     = r.order_id
        LEFT JOIN order_payments op ON o.order_id = op.order_id
        WHERE o.order_status = 'delivered';
        """
        df = self.service.execute_query(query)
        if df.empty:
            return {}
        return df.iloc[0].to_dict()

    def get_repeat_purchase_rate(self) -> dict:
        """The single most important KPI: what % of customers made a second purchase?"""
        query = """
        WITH customer_orders AS (
            SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS total_orders
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        )
        SELECT
            COUNT(*)                                                       AS total_unique_customers,
            SUM(CASE WHEN total_orders = 1 THEN 1 ELSE 0 END)             AS one_time_buyers,
            SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END)             AS repeat_buyers,
            ROUND(
                100.0 * SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 2
            )                                                              AS repeat_rate_pct,
            ROUND(AVG(total_orders), 2)                                    AS avg_orders_per_customer
        FROM customer_orders;
        """
        df = self.service.execute_query(query)
        if df.empty:
            return {}
        return df.iloc[0].to_dict()
