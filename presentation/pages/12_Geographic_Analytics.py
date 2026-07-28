import streamlit as st
from presentation.performance import get_backend, cached_query
from adapters.plotly_service import PlotlyService
from adapters.analytics_service import DatabaseError

st.title("🗺️ Geographic Analytics")
st.caption("Retention rates, revenue, and delivery performance across Brazilian states.")

backend = get_backend()

try:
    # ── Retention by state ────────────────────────────────────────────────────
    st.subheader("Customer Retention Rate by State")
    df_state = cached_query(backend.geography, "get_retention_by_state")
    if not df_state.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = PlotlyService.create_bar_chart(
                df_state.head(15), x="state", y="repeat_rate_pct",
                title="Top 15 States by Repeat Purchase Rate (%)",
                text="repeat_rate_pct",
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = PlotlyService.create_bar_chart(
                df_state.head(15), x="state", y="total_customers",
                title="Customer Volume by State",
                color="repeat_rate_pct",
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Revenue by state ──────────────────────────────────────────────────────
    st.subheader("Revenue by State")
    df_rev = cached_query(backend.geography, "get_revenue_by_state")
    if not df_rev.empty:
        fig3 = PlotlyService.create_bar_chart(
            df_rev.head(15), x="total_revenue", y="state",
            title="Top 15 States by Total Revenue (R$)",
            text="orders",
        )
        fig3.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ── Delivery delay by seller state ────────────────────────────────────────
    st.subheader("Delivery Delays by Seller State")
    df_delay = cached_query(backend.geography, "get_delivery_delay_by_state")
    if not df_delay.empty:
        fig4 = PlotlyService.create_bar_chart(
            df_delay.head(15), x="avg_delay_days", y="seller_state",
            title="Average Delivery Delay (days) by Seller State",
            text="late_delivery_pct",
        )
        fig4.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig4, use_container_width=True)
        st.info(
            "💡 States with high average delivery delays have higher churn rates. "
            "Logistics partnerships in key seller states can improve retention.",
            icon="💡",
        )

except DatabaseError as e:
    st.error(f"⚠️ Data unavailable: {e}")
