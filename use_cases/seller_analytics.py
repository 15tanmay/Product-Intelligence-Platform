import pandas as pd
from adapters.analytics_service import AnalyticsService


class SellerAnalytics:
    """Analyses seller performance and its impact on customer retention."""

    def __init__(self, service: AnalyticsService) -> None:
        self.service = service

    def get_seller_performance(self) -> pd.DataFrame:
        """Rank sellers by revenue, average review score, and on-time delivery rate."""
        query = """
        SELECT
            s.seller_id,
            s.seller_state,
            COUNT(DISTINCT oi.order_id)                               AS total_orders,
            ROUND(SUM(oi.price), 2)                                   AS total_revenue,
            ROUND(AVG(r.review_score), 2)                             AS avg_review_score,
            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN julianday(o.order_delivered_customer_date)
                             <= julianday(o.order_estimated_delivery_date)
                        THEN 1 ELSE 0
                    END
                ) / NULLIF(COUNT(DISTINCT oi.order_id), 0), 2
            )                                                         AS on_time_pct
        FROM sellers s
        JOIN order_items oi ON s.seller_id = oi.seller_id
        JOIN orders o       ON oi.order_id = o.order_id
        LEFT JOIN reviews r ON o.order_id  = r.order_id
        WHERE o.order_status = 'delivered'
          AND o.order_delivered_customer_date IS NOT NULL
        GROUP BY s.seller_id, s.seller_state
        HAVING total_orders >= 10
        ORDER BY total_revenue DESC
        LIMIT 30;
        """
        return self.service.execute_query(query)

    def get_seller_churn_impact(self) -> pd.DataFrame:
        """Low-rated sellers: churn rate grouped by seller average rating band.

        Uses a flat approach: aggregate seller ratings and customer order counts
        independently, then join once at the order level.
        """
        query = """
        SELECT
            CASE
                WHEN avg_score < 2  THEN 'Very Poor (< 2)'
                WHEN avg_score < 3  THEN 'Poor (2–3)'
                WHEN avg_score < 4  THEN 'Average (3–4)'
                ELSE                     'Good (4–5)'
            END                                     AS seller_rating_band,
            COUNT(*)                                AS total_records,
            SUM(is_one_time)                        AS one_time_buyers,
            ROUND(100.0 * SUM(is_one_time) / NULLIF(COUNT(*), 0), 2) AS churn_rate_pct
        FROM (
            SELECT
                c.customer_unique_id,
                AVG(r.review_score) AS avg_score,
                CASE WHEN COUNT(DISTINCT o.order_id) = 1 THEN 1 ELSE 0 END AS is_one_time
            FROM customers c
            JOIN orders o    ON c.customer_id  = o.customer_id
            JOIN order_items oi ON o.order_id  = oi.order_id
            JOIN reviews r   ON o.order_id     = r.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        ) sub
        GROUP BY seller_rating_band
        ORDER BY churn_rate_pct DESC;
        """
        return self.service.execute_query(query)
