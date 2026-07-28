import pandas as pd
from adapters.analytics_service import AnalyticsService


class ProductAnalytics:
    """Analyses product categories, pricing, and their impact on repeat purchases."""

    def __init__(self, service: AnalyticsService) -> None:
        self.service = service

    def get_top_categories_by_revenue(self) -> pd.DataFrame:
        """Revenue and order volume ranked by English category name."""
        query = """
        SELECT
            COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') AS category,
            COUNT(DISTINCT oi.order_id)                AS orders,
            ROUND(SUM(oi.price), 2)                    AS total_revenue,
            ROUND(AVG(oi.price), 2)                    AS avg_price,
            ROUND(AVG(r.review_score), 2)              AS avg_review_score
        FROM order_items oi
        JOIN orders o       ON oi.order_id   = o.order_id
        JOIN products p     ON oi.product_id = p.product_id
        LEFT JOIN product_category_name_translation t
                            ON p.product_category_name = t.product_category_name
        LEFT JOIN reviews r ON o.order_id    = r.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY category
        ORDER BY total_revenue DESC
        LIMIT 20;
        """
        return self.service.execute_query(query)

    def get_category_retention_rate(self) -> pd.DataFrame:
        """Which product categories are bought by repeat customers most often?"""
        query = """
        WITH customer_orders AS (
            SELECT
                c.customer_unique_id,
                COUNT(DISTINCT o.order_id) AS total_orders
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        ),
        category_purchases AS (
            SELECT
                c.customer_unique_id,
                COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') AS category
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN product_category_name_translation t
                ON p.product_category_name = t.product_category_name
            WHERE o.order_status = 'delivered'
        )
        SELECT
            cp.category,
            COUNT(cp.customer_unique_id)                AS total_buyers,
            SUM(CASE WHEN co.total_orders > 1 THEN 1 ELSE 0 END) AS repeat_buyers,
            ROUND(
                100.0 * SUM(CASE WHEN co.total_orders > 1 THEN 1 ELSE 0 END) /
                NULLIF(COUNT(cp.customer_unique_id), 0), 2
            )                                           AS repeat_rate_pct
        FROM category_purchases cp
        JOIN customer_orders co ON cp.customer_unique_id = co.customer_unique_id
        GROUP BY cp.category
        HAVING total_buyers >= 50
        ORDER BY repeat_rate_pct DESC
        LIMIT 20;
        """
        return self.service.execute_query(query)

    def get_price_band_retention(self) -> pd.DataFrame:
        """Does order value influence repeat purchase likelihood?"""
        query = """
        WITH order_value AS (
            SELECT
                o.order_id,
                c.customer_unique_id,
                SUM(oi.price + oi.freight_value) AS order_total
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY o.order_id, c.customer_unique_id
        ),
        customer_orders AS (
            SELECT customer_unique_id, COUNT(order_id) AS total_orders
            FROM order_value
            GROUP BY customer_unique_id
        )
        SELECT
            CASE
                WHEN ov.order_total < 50   THEN 'Under R$50'
                WHEN ov.order_total < 150  THEN 'R$50–150'
                WHEN ov.order_total < 300  THEN 'R$150–300'
                WHEN ov.order_total < 500  THEN 'R$300–500'
                ELSE 'Over R$500'
            END                                        AS price_band,
            CASE WHEN co.total_orders > 1 THEN 'Repeat' ELSE 'One-Time' END AS customer_type,
            COUNT(ov.customer_unique_id)               AS customers
        FROM order_value ov
        JOIN customer_orders co ON ov.customer_unique_id = co.customer_unique_id
        GROUP BY 1, 2
        ORDER BY 1, 2;
        """
        return self.service.execute_query(query)
