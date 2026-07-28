import streamlit as st
from presentation.performance import get_backend, cached_query
from adapters.plotly_service import PlotlyService
from adapters.analytics_service import DatabaseError

st.title("🏪 Seller Analytics")
st.caption("Seller performance rankings and seller quality impact on customer churn.")

backend = get_backend()

try:
    # ── Seller performance table ──────────────────────────────────────────────
    st.subheader("Top Sellers by Revenue")
    df_sellers = cached_query(backend.sellers, "get_seller_performance")
    if not df_sellers.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = PlotlyService.create_scatter(
                df_sellers, x="avg_review_score", y="on_time_pct",
                title="Seller Quality: Review Score vs On-Time Delivery %",
                color="total_revenue",
                size="total_orders",
                hover_data=["seller_id", "seller_state"],
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = PlotlyService.create_bar_chart(
                df_sellers.head(15), x="total_revenue", y="seller_id",
                title="Top 15 Sellers by Revenue (R$)",
            )
            fig2.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig2, use_container_width=True)

        with st.expander("📋 Full Seller Table"):
            st.dataframe(df_sellers, use_container_width=True)

    st.divider()

    # ── Seller rating band vs churn ───────────────────────────────────────────
    st.subheader("Seller Rating vs Customer Churn Rate")
    df_churn = cached_query(backend.sellers, "get_seller_churn_impact")
    if not df_churn.empty:
        fig3 = PlotlyService.create_bar_chart(
            df_churn, x="seller_rating_band", y="churn_rate_pct",
            title="One-Time Buyer Rate (%) by Seller Rating Band",
            text="churn_rate_pct",
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.warning(
            "⚠️ Sellers with average review scores below 3 have significantly higher "
            "customer churn rates. Seller quality standards directly impact retention.",
        )

except DatabaseError as e:
    st.error(f"⚠️ Data unavailable: {e}")
