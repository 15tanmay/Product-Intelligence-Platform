import pandas as pd
from adapters.analytics_service import AnalyticsService


class RetentionAnalytics:
    """Analyses drivers of first-time customer churn using delivery, review,
    and payment data from the full Olist dataset."""

    def __init__(self, service: AnalyticsService) -> None:
        self.service = service

    def analyze_delivery_impact(self) -> pd.DataFrame:
        """Delivery experience (on-time vs late) broken down by repeat vs one-time status."""
        query = """
        WITH order_delays AS (
            SELECT
                c.customer_unique_id,
                o.order_id,
                julianday(o.order_delivered_customer_date)
                    - julianday(o.order_estimated_delivery_date) AS delay_days
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
              AND o.order_delivered_customer_date IS NOT NULL
        ),
        customer_repeats AS (
            SELECT customer_unique_id, COUNT(order_id) AS total_orders
            FROM order_delays
            GROUP BY customer_unique_id
        )
        SELECT
            CASE WHEN d.delay_days > 0 THEN 'Late Delivery' ELSE 'On-Time/Early' END AS delivery_experience,
            CASE WHEN r.total_orders  > 1 THEN 'Repeat' ELSE 'One-Time' END          AS customer_type,
            COUNT(d.customer_unique_id)                                               AS customers
        FROM order_delays d
        JOIN customer_repeats r ON d.customer_unique_id = r.customer_unique_id
        GROUP BY 1, 2;
        """
        return self.service.execute_query(query)

    def get_review_score_vs_retention(self) -> pd.DataFrame:
        """Does review score on the first order predict whether a customer returns?"""
        query = """
        WITH first_orders AS (
            SELECT
                c.customer_unique_id,
                MIN(o.order_purchase_timestamp) AS first_purchase_ts
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        ),
        first_order_ids AS (
            SELECT fo.customer_unique_id, o.order_id
            FROM first_orders fo
            JOIN orders o ON o.order_purchase_timestamp = fo.first_purchase_ts
            JOIN customers c ON c.customer_id = o.customer_id
                             AND c.customer_unique_id = fo.customer_unique_id
        ),
        customer_totals AS (
            SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS total_orders
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        )
        SELECT
            r.review_score,
            COUNT(foi.customer_unique_id)                            AS customers,
            SUM(CASE WHEN ct.total_orders > 1 THEN 1 ELSE 0 END)   AS repeat_buyers,
            ROUND(
                100.0 * SUM(CASE WHEN ct.total_orders > 1 THEN 1 ELSE 0 END)
                / NULLIF(COUNT(foi.customer_unique_id), 0), 2
            )                                                        AS repeat_rate_pct
        FROM first_order_ids foi
        JOIN reviews r ON foi.order_id = r.order_id
        JOIN customer_totals ct ON foi.customer_unique_id = ct.customer_unique_id
        GROUP BY r.review_score
        ORDER BY r.review_score;
        """
        return self.service.execute_query(query)

    def get_time_to_second_purchase(self) -> pd.DataFrame:
        """Distribution of days between first and second purchase for repeat customers."""
        query = """
        WITH ranked_orders AS (
            SELECT
                c.customer_unique_id,
                o.order_purchase_timestamp,
                ROW_NUMBER() OVER (
                    PARTITION BY c.customer_unique_id
                    ORDER BY o.order_purchase_timestamp
                ) AS order_rank
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_status = 'delivered'
        ),
        first_second AS (
            SELECT
                r1.customer_unique_id,
                julianday(r2.order_purchase_timestamp)
                    - julianday(r1.order_purchase_timestamp) AS days_to_second
            FROM ranked_orders r1
            JOIN ranked_orders r2
              ON r1.customer_unique_id = r2.customer_unique_id
             AND r1.order_rank = 1
             AND r2.order_rank = 2
        )
        SELECT
            CASE
                WHEN days_to_second <=  30 THEN '0–30 days'
                WHEN days_to_second <=  90 THEN '31–90 days'
                WHEN days_to_second <= 180 THEN '91–180 days'
                WHEN days_to_second <= 365 THEN '181–365 days'
                ELSE 'Over 1 year'
            END                            AS time_band,
            COUNT(customer_unique_id)      AS customers
        FROM first_second
        GROUP BY 1
        ORDER BY MIN(days_to_second);
        """
        return self.service.execute_query(query)
