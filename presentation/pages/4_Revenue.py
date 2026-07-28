import streamlit as st
from presentation.performance import get_backend, cached_query
from adapters.plotly_service import PlotlyService
from adapters.analytics_service import DatabaseError

st.title("💰 Revenue Analytics")
st.caption("Monthly revenue trends and revenue by customer segment.")

backend = get_backend()

try:
    # ── Monthly revenue trend ────────────────────────────────────────────────
    df_monthly = cached_query(backend.revenue, "get_monthly_revenue")
    if not df_monthly.empty:
        fig = PlotlyService.create_line_chart(
            df_monthly, x="month", y="total_revenue",
            title="Monthly Gross Revenue (R$) — Delivered Orders",
        )
        st.plotly_chart(fig, use_container_width=True)

        # secondary: avg order value over time
        fig2 = PlotlyService.create_line_chart(
            df_monthly, x="month", y="avg_order_value",
            title="Average Order Value (R$) Over Time",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Revenue by customer type ─────────────────────────────────────────────
    st.subheader("Revenue: One-Time vs Repeat Customers")
    df_by_type = cached_query(backend.revenue, "get_revenue_by_customer_type")
    if not df_by_type.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig3 = PlotlyService.create_bar_chart(
                df_by_type, x="customer_type", y="total_revenue",
                title="Total Revenue by Customer Type",
            )
            st.plotly_chart(fig3, use_container_width=True)
        with col2:
            fig4 = PlotlyService.create_bar_chart(
                df_by_type, x="customer_type", y="avg_lifetime_value",
                title="Average Lifetime Value (R$)",
            )
            st.plotly_chart(fig4, use_container_width=True)

        st.info(
            "💡 Even though repeat customers are a minority, they typically generate "
            "significantly higher lifetime value per customer.",
            icon="💡",
        )

except DatabaseError as e:
    st.error(f"⚠️ Data unavailable: {e}")
