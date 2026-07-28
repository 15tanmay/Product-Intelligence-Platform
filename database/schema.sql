-- ============================================================
-- Product Intelligence Platform — SQLite Schema
-- Dataset: Olist Brazilian E-Commerce (9 tables)
-- Primary Question: Why are first-time customers not becoming
-- repeat customers?
-- ============================================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT NOT NULL,
    customer_zip_code_prefix TEXT,
    customer_city TEXT,
    customer_state TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    order_status TEXT,
    order_purchase_timestamp DATETIME,
    order_approved_at DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id TEXT,
    order_item_id INTEGER,
    product_id TEXT,
    seller_id TEXT,
    shipping_limit_date DATETIME,
    price REAL,
    freight_value REAL,
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id),
    FOREIGN KEY(seller_id) REFERENCES sellers(seller_id)
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id TEXT,
    order_id TEXT,
    review_score INTEGER,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date DATETIME,
    review_answer_timestamp DATETIME,
    PRIMARY KEY(review_id, order_id),
    FOREIGN KEY(order_id) REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS order_payments (
    order_id TEXT,
    payment_sequential INTEGER,
    payment_type TEXT,
    payment_installments INTEGER,
    payment_value REAL,
    PRIMARY KEY(order_id, payment_sequential),
    FOREIGN KEY(order_id) REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g REAL,
    product_length_cm REAL,
    product_height_cm REAL,
    product_width_cm REAL
);

CREATE TABLE IF NOT EXISTS sellers (
    seller_id TEXT PRIMARY KEY,
    seller_zip_code_prefix TEXT,
    seller_city TEXT,
    seller_state TEXT
);

CREATE TABLE IF NOT EXISTS geolocation (
    geolocation_zip_code_prefix TEXT,
    geolocation_lat REAL,
    geolocation_lng REAL,
    geolocation_city TEXT,
    geolocation_state TEXT
);

CREATE TABLE IF NOT EXISTS product_category_name_translation (
    product_category_name TEXT PRIMARY KEY,
    product_category_name_english TEXT
);

-- ============================================================
-- Indexes for query performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_orders_customer      ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status        ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_purchase_ts   ON orders(order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_order_items_product  ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_seller   ON order_items(seller_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order    ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_reviews_order        ON reviews(order_id);
CREATE INDEX IF NOT EXISTS idx_reviews_score        ON reviews(review_score);
CREATE INDEX IF NOT EXISTS idx_payments_order       ON order_payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_type        ON order_payments(payment_type);
CREATE INDEX IF NOT EXISTS idx_products_category    ON products(product_category_name);
CREATE INDEX IF NOT EXISTS idx_customers_unique     ON customers(customer_unique_id);
CREATE INDEX IF NOT EXISTS idx_customers_state      ON customers(customer_state);
CREATE INDEX IF NOT EXISTS idx_customers_zip        ON customers(customer_zip_code_prefix);
CREATE INDEX IF NOT EXISTS idx_sellers_state        ON sellers(seller_state);
CREATE INDEX IF NOT EXISTS idx_sellers_zip          ON sellers(seller_zip_code_prefix);
CREATE INDEX IF NOT EXISTS idx_geolocation_zip      ON geolocation(geolocation_zip_code_prefix);
CREATE INDEX IF NOT EXISTS idx_geolocation_state    ON geolocation(geolocation_state);
CREATE INDEX IF NOT EXISTS idx_category_trans_name  ON product_category_name_translation(product_category_name);
