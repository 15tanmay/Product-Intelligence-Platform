import pandas as pd
from app_logging.logger import get_logger

logger = get_logger(__name__)

class FeatureEngineer:
    @staticmethod
    def add_delivery_delta(df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Calculating delivery delay features...")
        df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])
        df['delivery_delta_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days
        df['is_late'] = (df['delivery_delta_days'] > 0).astype(int)
        return df
