import pandas as pd
from adapters.analytics_service import AnalyticsService


class RecommendationEngine:
    """Identifies products and categories associated with repeat customer behaviour."""

    def __init__(self, service: AnalyticsService) -> None:
        self.service = service

    def get_top_products_for_retention(self) -> pd.DataFrame:
        """Products bought most by repeat customers, with category and review data."""
        query = """
        WITH repeat_customers AS (
            SELECT c.customer_unique_id
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
            HAVING COUNT(DISTINCT o.order_id) > 1
        )
        SELECT
            oi.product_id,
            COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') AS category,
            COUNT(DISTINCT oi.order_id)                         AS purchase_count,
            ROUND(AVG(oi.price), 2)                            AS avg_price,
            COUNT(DISTINCT CASE WHEN r.review_score >= 4
                           THEN r.review_id END)               AS positive_reviews,
            ROUND(AVG(r.review_score), 2)                      AS avg_review
        FROM order_items oi
        JOIN orders o    ON oi.order_id   = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN repeat_customers rc ON c.customer_unique_id = rc.customer_unique_id
        LEFT JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN product_category_name_translation t
            ON p.product_category_name = t.product_category_name
        LEFT JOIN reviews r ON o.order_id = r.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY oi.product_id, category
        ORDER BY purchase_count DESC
        LIMIT 15;
        """
        return self.service.execute_query(query)

    def get_high_retention_categories(self) -> pd.DataFrame:
        """Which product categories generate the highest proportion of repeat buyers?"""
        query = """
        WITH customer_orders AS (
            SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS total_orders
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        )
        SELECT
            COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') AS category,
            COUNT(DISTINCT c.customer_unique_id)                 AS total_buyers,
            SUM(CASE WHEN co.total_orders > 1 THEN 1 ELSE 0 END) AS repeat_buyers,
            ROUND(
                100.0 * SUM(CASE WHEN co.total_orders > 1 THEN 1 ELSE 0 END)
                / NULLIF(COUNT(DISTINCT c.customer_unique_id), 0), 2
            )                                                   AS retention_rate_pct
        FROM order_items oi
        JOIN orders o    ON oi.order_id   = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN customer_orders co ON c.customer_unique_id = co.customer_unique_id
        LEFT JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN product_category_name_translation t
            ON p.product_category_name = t.product_category_name
        WHERE o.order_status = 'delivered'
        GROUP BY category
        HAVING total_buyers >= 30
        ORDER BY retention_rate_pct DESC
        LIMIT 15;
        """
        return self.service.execute_query(query)
