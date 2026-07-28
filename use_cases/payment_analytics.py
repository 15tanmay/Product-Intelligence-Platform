import pandas as pd
from adapters.analytics_service import AnalyticsService


class PaymentAnalytics:
    """Analyses payment methods, installment patterns, and their relationship
    to first-time vs repeat customer behaviour."""

    def __init__(self, service: AnalyticsService) -> None:
        self.service = service

    def get_payment_method_distribution(self) -> pd.DataFrame:
        """Return order counts and revenue grouped by payment type."""
        query = """
        SELECT
            op.payment_type,
            COUNT(DISTINCT op.order_id)               AS order_count,
            ROUND(SUM(op.payment_value), 2)            AS total_revenue,
            ROUND(AVG(op.payment_value), 2)            AS avg_order_value
        FROM order_payments op
        JOIN orders o ON op.order_id = o.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY op.payment_type
        ORDER BY order_count DESC;
        """
        return self.service.execute_query(query)

    def get_installment_vs_retention(self) -> pd.DataFrame:
        """Analyse whether high installment counts correlate with churn."""
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
        payment_profile AS (
            SELECT
                c.customer_unique_id,
                AVG(op.payment_installments) AS avg_installments
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_payments op ON o.order_id = op.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        )
        SELECT
            CASE
                WHEN pp.avg_installments = 1  THEN '1 (No Installment)'
                WHEN pp.avg_installments <= 3 THEN '2-3 Installments'
                WHEN pp.avg_installments <= 6 THEN '4-6 Installments'
                ELSE '7+ Installments'
            END                                        AS installment_band,
            CASE WHEN co.total_orders = 1 THEN 'One-Time' ELSE 'Repeat' END AS customer_type,
            COUNT(pp.customer_unique_id)               AS customers
        FROM payment_profile pp
        JOIN customer_orders co ON pp.customer_unique_id = co.customer_unique_id
        GROUP BY 1, 2
        ORDER BY 1, 2;
        """
        return self.service.execute_query(query)
