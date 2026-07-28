import streamlit as st
from presentation.performance import get_backend, cached_query
from adapters.plotly_service import PlotlyService
from adapters.analytics_service import DatabaseError

st.title("👥 Customer Analytics")
st.caption("First-time vs repeat customer breakdown and customer lifecycle analysis.")

backend = get_backend()

try:
    col1, col2 = st.columns(2)

    # ── First vs Repeat ratio ────────────────────────────────────────────────
    with col1:
        df_ratio = cached_query(backend.customer, "get_first_vs_repeat_ratio")
        if not df_ratio.empty:
            fig = PlotlyService.create_pie_chart(
                df_ratio, names="customer_type", values="count",
                title="First-Time vs Repeat Customers",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Cohort retention heatmap ─────────────────────────────────────────────
    with col2:
        df_cohort = cached_query(backend.cohorts, "get_monthly_cohorts")
        if not df_cohort.empty:
            import pandas as pd
            pivot = df_cohort.pivot_table(
                index="cohort_month", columns="purchase_month",
                values="active_customers", fill_value=0,
            )
            # Show only cohorts with data (last 24 months)
            pivot = pivot.tail(16)
            fig_heat = PlotlyService.create_heatmap(
                pivot,
                title="Monthly Cohort Retention",
                x_label="Purchase Month",
                y_label="Cohort (First Purchase Month)",
            )
            st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()

    # ── RFM distribution ─────────────────────────────────────────────────────
    st.subheader("RFM Customer Segments")
    df_rfm = cached_query(backend.segmentation, "get_rfm_segments")
    if not df_rfm.empty:
        seg_counts = df_rfm["RFM_Segment"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Count"]
        fig_seg = PlotlyService.create_bar_chart(
            seg_counts.head(12), x="Segment", y="Count",
            title="Top 12 RFM Segments",
        )
        st.plotly_chart(fig_seg, use_container_width=True)

        with st.expander("📋 RFM Data Table"):
            st.dataframe(
                df_rfm[["customer_unique_id", "recency_days", "frequency",
                         "monetary_value", "RFM_Segment"]].head(500),
                use_container_width=True,
            )

except DatabaseError as e:
    st.error(f"⚠️ Data unavailable: {e}")
