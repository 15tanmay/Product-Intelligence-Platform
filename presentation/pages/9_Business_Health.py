import streamlit as st
from presentation.performance import get_backend
from adapters.analytics_service import DatabaseError
from database.db import get_connection

st.title("🏥 Business Health")
st.caption("Data quality, table statistics, and system status.")

try:
    with get_connection() as conn:
        tables = [
            "customers", "orders", "order_items", "order_payments",
            "reviews", "products", "sellers", "geolocation",
            "product_category_name_translation",
        ]

        st.subheader("📊 Database Table Row Counts")
        cols = st.columns(3)
        for i, table in enumerate(tables):
            try:
                result = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                count = result[0] if result else 0
                cols[i % 3].metric(table.replace("_", " ").title(), f"{count:,}")
            except Exception:
                cols[i % 3].metric(table.replace("_", " ").title(), "Not found")

        st.divider()

        st.subheader("🔍 Data Quality Checks")
        checks = {
            "Orders with NULL delivered date":
                "SELECT COUNT(*) FROM orders WHERE order_delivered_customer_date IS NULL",
            "Orders with NULL estimated date":
                "SELECT COUNT(*) FROM orders WHERE order_estimated_delivery_date IS NULL",
            "Order items with NULL product_id":
                "SELECT COUNT(*) FROM order_items WHERE product_id IS NULL",
            "Reviews with NULL score":
                "SELECT COUNT(*) FROM reviews WHERE review_score IS NULL",
            "Customers with NULL state":
                "SELECT COUNT(*) FROM customers WHERE customer_state IS NULL",
        }

        for label, query in checks.items():
            try:
                result = conn.execute(query).fetchone()
                count = result[0] if result else 0
                status = "✅" if count == 0 else "⚠️"
                st.write(f"{status} **{label}:** {count:,} rows")
            except Exception as ex:
                st.write(f"❌ **{label}:** Error — {ex}")

        st.divider()

        st.subheader("ℹ️ System Info")
        st.info(
            "Database: SQLite  |  Dataset: Olist Brazilian E-Commerce  |  "
            "Platform: Product Intelligence Platform v2.0",
            icon="ℹ️",
        )

except Exception as e:
    st.error(f"⚠️ Could not connect to database: {e}")
