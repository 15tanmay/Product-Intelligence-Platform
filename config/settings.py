from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"
DB_PATH = BASE_DIR / "product_intelligence.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

KAGGLE_DATASET = "olistbr/brazilian-ecommerce"

# Maps SQLite table name -> source CSV filename in data/raw/
# Geolocation is excluded from incremental PK-based upsert (no single PK),
# so it is loaded last with replace strategy.
DATASET_FILES = {
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "product_category_name_translation": "product_category_name_translation.csv",
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
}

# Tables loaded with full replace (no stable single primary key)
REPLACE_ONLY_TABLES = {
    "geolocation": "olist_geolocation_dataset.csv",
}
