import pandas as pd
from adapters.analytics_service import AnalyticsService


class GeographicAnalytics:
    """Geographic analysis of customer retention patterns across Brazilian states."""

    def __init__(self, service: AnalyticsService) -> None:
        self.service = service

    def get_retention_by_state(self) -> pd.DataFrame:
        """First-time vs repeat customer ratio broken down by customer state."""
        query = """
        WITH customer_orders AS (
            SELECT
                c.customer_unique_id,
                c.customer_state,
                COUNT(DISTINCT o.order_id) AS total_orders
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id, c.customer_state
        )
        SELECT
            customer_state                             AS state,
            COUNT(customer_unique_id)                  AS total_customers,
            SUM(CASE WHEN total_orders = 1 THEN 1 ELSE 0 END) AS one_time_buyers,
            SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) AS repeat_buyers,
            ROUND(
                100.0 * SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END)
                / NULLIF(COUNT(customer_unique_id), 0), 2
            )                                          AS repeat_rate_pct
        FROM customer_orders
        GROUP BY customer_state
        ORDER BY total_customers DESC;
        """
        return self.service.execute_query(query)

    def get_revenue_by_state(self) -> pd.DataFrame:
        """Revenue contribution ranked by state."""
        query = """
        SELECT
            c.customer_state                           AS state,
            COUNT(DISTINCT o.order_id)                 AS orders,
            ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,
            ROUND(AVG(oi.price + oi.freight_value), 2) AS avg_order_value
        FROM customers c
        JOIN orders o    ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_state
        ORDER BY total_revenue DESC;
        """
        return self.service.execute_query(query)

    def get_delivery_delay_by_state(self) -> pd.DataFrame:
        """Average delivery delay (actual vs estimated) by seller state."""
        query = """
        SELECT
            s.seller_state,
            COUNT(DISTINCT o.order_id)                  AS orders,
            ROUND(
                AVG(julianday(o.order_delivered_customer_date)
                    - julianday(o.order_estimated_delivery_date)), 2
            )                                           AS avg_delay_days,
            ROUND(
                100.0 * SUM(
                    CASE WHEN julianday(o.order_delivered_customer_date)
                              > julianday(o.order_estimated_delivery_date)
                         THEN 1 ELSE 0 END
                ) / NULLIF(COUNT(DISTINCT o.order_id), 0), 2
            )                                           AS late_delivery_pct
        FROM sellers s
        JOIN order_items oi ON s.seller_id = oi.seller_id
        JOIN orders o       ON oi.order_id = o.order_id
        WHERE o.order_status = 'delivered'
          AND o.order_delivered_customer_date IS NOT NULL
        GROUP BY s.seller_state
        HAVING orders >= 20
        ORDER BY avg_delay_days DESC;
        """
        return self.service.execute_query(query)
