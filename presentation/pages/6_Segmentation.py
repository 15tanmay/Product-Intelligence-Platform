import streamlit as st
from presentation.performance import get_backend, cached_query
from adapters.plotly_service import PlotlyService
from adapters.analytics_service import DatabaseError

st.title("🗂️ Customer Segmentation")
st.caption("RFM-based segmentation to identify at-risk and loyal customer groups.")

backend = get_backend()

try:
    df_rfm = cached_query(backend.segmentation, "get_rfm_segments")

    if not df_rfm.empty:
        # ── Segment summary bar ───────────────────────────────────────────────
        seg_counts = df_rfm["RFM_Segment"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Count"]
        fig = PlotlyService.create_bar_chart(
            seg_counts.head(12), x="Segment", y="Count",
            title="Top 12 RFM Segments by Customer Count",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # ── Scatter: Recency vs Monetary ─────────────────────────────────────
        st.subheader("Recency vs Lifetime Value")
        fig2 = PlotlyService.create_scatter(
            df_rfm.head(2000), x="recency_days", y="monetary_value",
            title="Customer Recency vs Monetary Value",
            color="RFM_Segment",
            hover_data=["frequency"],
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # ── Frequency distribution ────────────────────────────────────────────
        st.subheader("Purchase Frequency Distribution")
        freq_dist = df_rfm["frequency"].value_counts().reset_index()
        freq_dist.columns = ["frequency", "customers"]
        freq_dist = freq_dist[freq_dist["frequency"] <= 10].sort_values("frequency")
        fig3 = PlotlyService.create_bar_chart(
            freq_dist, x="frequency", y="customers",
            title="Number of Orders per Customer",
        )
        st.plotly_chart(fig3, use_container_width=True)

except DatabaseError as e:
    st.error(f"⚠️ Data unavailable: {e}")
