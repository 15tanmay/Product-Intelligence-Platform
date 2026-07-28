import pandas as pd
from adapters.analytics_service import AnalyticsService
from core.business_rules import BusinessRules


class BusinessInsights:
    """Generates plain-language executive insights from the data."""

    def __init__(self, service: AnalyticsService) -> None:
        self.service = service

    def generate_retention_insight(self) -> str:
        """Late delivery rate and its implication for churn."""
        query = """
        SELECT
            julianday(order_delivered_customer_date)
                - julianday(order_estimated_delivery_date) AS delay
        FROM orders
        WHERE order_status = 'delivered'
          AND order_delivered_customer_date IS NOT NULL
        """
        df = self.service.execute_query(query)
        if df.empty:
            return "No delivery data available to generate insights."
        late_pct = (df["delay"] > BusinessRules.LATE_DELIVERY_TOLERANCE_DAYS).mean() * 100
        return (
            f"[Insight] {late_pct:.1f}% of delivered orders arrived later than estimated. "
            "Late deliveries strongly correlate with first-time customer churn."
        )

    def generate_review_insight(self) -> str:
        """Average first-order review score and its link to repeat purchases."""
        query = """
        WITH first_orders AS (
            SELECT c.customer_unique_id, MIN(o.order_purchase_timestamp) AS first_ts
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        ),
        first_reviews AS (
            SELECT fo.customer_unique_id, r.review_score
            FROM first_orders fo
            JOIN orders o ON o.order_purchase_timestamp = fo.first_ts
            JOIN customers c ON c.customer_id = o.customer_id
                             AND c.customer_unique_id = fo.customer_unique_id
            JOIN reviews r ON r.order_id = o.order_id
        )
        SELECT AVG(review_score) AS avg_first_review
        FROM first_reviews;
        """
        df = self.service.execute_query(query)
        if df.empty or df["avg_first_review"].isna().all():
            return "Insufficient review data."
        avg = df["avg_first_review"].iloc[0]
        return (
            f"[Insight] Average first-order review score is {avg:.2f}/5. "
            "Customers who rate their first order <= 3 are significantly less likely to repurchase."
        )

    def generate_repeat_rate_insight(self, repeat_rate_pct: float | None = None) -> str:
        """Headline repeat purchase rate insight."""
        if repeat_rate_pct is None:
            query = """
            WITH co AS (
                SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS n
                FROM customers c JOIN orders o ON c.customer_id = o.customer_id
                WHERE o.order_status = 'delivered'
                GROUP BY c.customer_unique_id
            )
            SELECT ROUND(100.0 * SUM(CASE WHEN n > 1 THEN 1 ELSE 0 END)
                   / NULLIF(COUNT(*), 0), 2) AS rate
            FROM co;
            """
            df = self.service.execute_query(query)
            repeat_rate_pct = df["rate"].iloc[0] if not df.empty else 0.0
        return (
            f"[Insight] Only {repeat_rate_pct:.1f}% of customers made a second purchase. "
            "Improving delivery reliability and post-purchase experience are the highest-leverage levers."
        )
