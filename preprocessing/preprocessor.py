import pandas as pd
from app_logging.logger import get_logger

logger = get_logger(__name__)

class DataPreprocessor:
    @staticmethod
    def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Cleaning orders data...")
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
        df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
        df = df[df['order_status'] == 'delivered'].copy()
        return df

    @staticmethod
    def handle_missing(df: pd.DataFrame, subset: list) -> pd.DataFrame:
        logger.info(f"Dropping missing values in {subset}")
        return df.dropna(subset=subset)
