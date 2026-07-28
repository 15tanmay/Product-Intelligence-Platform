"""Shared dataset schema constants.

Centralises column expectations and primary key definitions so both
loader.py and validator.py can import them without circular dependencies.
"""

# Maps SQLite table name -> list of required CSV column names
EXPECTED_COLUMNS: dict[str, list[str]] = {
    "customers": [
        "customer_id", "customer_unique_id", "customer_zip_code_prefix",
        "customer_city", "customer_state",
    ],
    "orders": [
        "order_id", "customer_id", "order_status",
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": [
        "order_id", "order_item_id", "product_id", "seller_id",
        "shipping_limit_date", "price", "freight_value",
    ],
    "order_payments": [
        "order_id", "payment_sequential", "payment_type",
        "payment_installments", "payment_value",
    ],
    "reviews": [
        "review_id", "order_id", "review_score",
        "review_comment_title", "review_comment_message",
        "review_creation_date", "review_answer_timestamp",
    ],
    "products": [
        "product_id", "product_category_name",
        "product_name_lenght", "product_description_lenght",
        "product_photos_qty", "product_weight_g",
        "product_length_cm", "product_height_cm", "product_width_cm",
    ],
    "sellers": [
        "seller_id", "seller_zip_code_prefix", "seller_city", "seller_state",
    ],
    "geolocation": [
        "geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng",
        "geolocation_city", "geolocation_state",
    ],
    "product_category_name_translation": [
        "product_category_name", "product_category_name_english",
    ],
}

# Maps table name -> primary key column(s)
PRIMARY_KEYS: dict[str, list[str]] = {
    "customers": ["customer_id"],
    "orders": ["order_id"],
    "order_items": ["order_id", "order_item_id"],
    "order_payments": ["order_id", "payment_sequential"],
    "reviews": ["review_id", "order_id"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "product_category_name_translation": ["product_category_name"],
    # geolocation has no stable PK
}

# Critical not-null columns per table
CRITICAL_COLUMNS: dict[str, list[str]] = {
    "customers": ["customer_id", "customer_unique_id"],
    "orders": ["order_id", "customer_id", "order_status"],
    "order_items": ["order_id", "order_item_id", "product_id", "seller_id", "price", "freight_value"],
    "order_payments": ["order_id", "payment_value"],
    "reviews": ["review_id", "order_id", "review_score"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "geolocation": ["geolocation_zip_code_prefix"],
    "product_category_name_translation": ["product_category_name"],
}
