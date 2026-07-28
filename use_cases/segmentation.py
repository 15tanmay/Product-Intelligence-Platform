import pandas as pd
from adapters.analytics_service import AnalyticsService

class SegmentationAnalytics:
    def __init__(self, service: AnalyticsService):
        self.service = service

    def get_rfm_segments(self) -> pd.DataFrame:
        query = """
        SELECT 
            c.customer_unique_id,
            julianday('now') - julianday(MAX(o.order_purchase_timestamp)) as recency_days,
            COUNT(DISTINCT o.order_id) as frequency,
            SUM(oi.price) as monetary_value
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_unique_id;
        """
        df = self.service.execute_query(query)
        if not df.empty:
            df['R_Score'] = pd.qcut(df['recency_days'], 4, labels=[4, 3, 2, 1], duplicates='drop')
            df['F_Score'] = df['frequency'].apply(lambda x: 4 if x > 2 else (3 if x == 2 else 1))
            df['M_Score'] = pd.qcut(df['monetary_value'], 4, labels=[1, 2, 3, 4], duplicates='drop')
            df['RFM_Segment'] = df['R_Score'].astype(str) + df['F_Score'].astype(str) + df['M_Score'].astype(str)
        return df
