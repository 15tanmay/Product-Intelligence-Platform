import streamlit as st
from presentation.performance import get_backend, cached_query
from adapters.plotly_service import PlotlyService
from adapters.analytics_service import DatabaseError
from use_cases.recommendation_engine import RecommendationEngine

st.title("🎯 Recommendation Center")
st.caption("Products and categories that drive repeat purchases — actionable insights for the product team.")

backend = get_backend()

try:
    # ── Top retention products ────────────────────────────────────────────────
    st.subheader("Top Products Purchased by Repeat Customers")
    df_prod = cached_query(backend.recommendations, "get_top_products_for_retention")
    if not df_prod.empty:
        fig = PlotlyService.create_bar_chart(
            df_prod, x="purchase_count", y="product_id",
            title="Most-Purchased Products Among Repeat Customers",
            color="avg_review",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Full Product Table"):
            st.dataframe(df_prod, use_container_width=True)

    st.divider()

    # ── High retention categories ─────────────────────────────────────────────
    st.subheader("Categories with Highest Repeat Purchase Rates")
    df_cat = cached_query(backend.recommendations, "get_high_retention_categories")
    if not df_cat.empty:
        fig2 = PlotlyService.create_bar_chart(
            df_cat, x="retention_rate_pct", y="category",
            title="Category Retention Rate (%) — min 30 buyers",
            text="repeat_buyers",
        )
        fig2.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

        st.info(
            "💡 Prioritise marketing and post-purchase campaigns in these high-retention "
            "categories to maximise second-purchase conversion.",
            icon="💡",
        )

except DatabaseError as e:
    st.error(f"⚠️ Data unavailable: {e}")
