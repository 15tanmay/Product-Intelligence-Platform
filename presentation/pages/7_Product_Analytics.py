import streamlit as st
from presentation.performance import get_backend, cached_query
from adapters.plotly_service import PlotlyService
from adapters.analytics_service import DatabaseError

st.title("📦 Product Analytics")
st.caption("Category performance, pricing bands, and their impact on repeat purchases.")

backend = get_backend()

try:
    # ── Top categories by revenue ─────────────────────────────────────────────
    st.subheader("Top Product Categories by Revenue")
    df_cat = cached_query(backend.products, "get_top_categories_by_revenue")
    if not df_cat.empty:
        fig = PlotlyService.create_bar_chart(
            df_cat.head(15), x="total_revenue", y="category",
            title="Top 15 Categories — Total Revenue (R$)",
            text="orders",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Category retention rate ───────────────────────────────────────────────
    st.subheader("Repeat Purchase Rate by Category")
    df_ret = cached_query(backend.products, "get_category_retention_rate")
    if not df_ret.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig2 = PlotlyService.create_bar_chart(
                df_ret.head(15), x="repeat_rate_pct", y="category",
                title="Top 15 Categories by Repeat Rate (%)",
                text="repeat_rate_pct",
            )
            fig2.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            fig3 = PlotlyService.create_scatter(
                df_ret, x="total_buyers", y="repeat_rate_pct",
                title="Volume vs Repeat Rate",
                color="repeat_rate_pct",
                hover_data=["category", "repeat_buyers"],
            )
            st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ── Price band vs retention ───────────────────────────────────────────────
    st.subheader("Order Value Band vs Customer Retention")
    df_price = cached_query(backend.products, "get_price_band_retention")
    if not df_price.empty:
        fig4 = PlotlyService.create_grouped_bar(
            df_price, x="price_band", y="customers",
            color="customer_type",
            title="One-Time vs Repeat Buyers by Order Value",
        )
        st.plotly_chart(fig4, use_container_width=True)

except DatabaseError as e:
    st.error(f"⚠️ Data unavailable: {e}")
