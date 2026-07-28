import streamlit as st
from presentation.performance import get_backend, cached_query
from adapters.plotly_service import PlotlyService
from adapters.analytics_service import DatabaseError

st.title("🔄 Retention Analytics")
st.caption("Deep dive into the drivers of first-time customer churn.")

backend = get_backend()

try:
    # ── Delivery impact ───────────────────────────────────────────────────────
    st.subheader("Delivery Experience vs Repeat Purchase")
    df_delivery = cached_query(backend.retention, "analyze_delivery_impact")
    if not df_delivery.empty:
        fig = PlotlyService.create_grouped_bar(
            df_delivery, x="delivery_experience", y="customers",
            color="customer_type",
            title="Delivery Experience: One-Time vs Repeat Customers",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Review score vs repeat purchase ──────────────────────────────────────
    st.subheader("First-Order Review Score vs Repeat Purchase Rate")
    df_review = cached_query(backend.retention, "get_review_score_vs_retention")
    if not df_review.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig2 = PlotlyService.create_bar_chart(
                df_review, x="review_score", y="repeat_rate_pct",
                title="Repeat Rate (%) by First-Order Review Score",
                text="repeat_rate_pct",
            )
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            fig3 = PlotlyService.create_bar_chart(
                df_review, x="review_score", y="customers",
                title="Customer Volume by First Review Score",
            )
            st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ── Time to second purchase ───────────────────────────────────────────────
    st.subheader("Time to Second Purchase (Repeat Customers Only)")
    df_t2p = cached_query(backend.retention, "get_time_to_second_purchase")
    if not df_t2p.empty:
        fig4 = PlotlyService.create_bar_chart(
            df_t2p, x="time_band", y="customers",
            title="Days Between 1st and 2nd Purchase",
            text="customers",
        )
        st.plotly_chart(fig4, use_container_width=True)

except DatabaseError as e:
    st.error(f"⚠️ Data unavailable: {e}")
