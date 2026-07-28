import streamlit as st
from presentation.performance import get_backend, cached_query
from presentation.streamlit_utils import StreamlitUtils
from adapters.analytics_service import DatabaseError

st.title("📊 Executive Summary")
st.caption("Core business question: Why are first-time customers not becoming repeat customers?")

backend = get_backend()

try:
    # ── KPI strip ────────────────────────────────────────────────────────────
    kpis = cached_query(backend.kpis, "get_high_level_metrics")
    repeat_kpis = cached_query(backend.kpis, "get_repeat_purchase_rate")

    if kpis:
        StreamlitUtils.display_kpi_row({
            "Total Customers":  int(kpis.get("total_customers", 0)),
            "Total Orders":     int(kpis.get("total_orders", 0)),
            "Total Revenue (R$)": kpis.get("total_revenue", 0.0),
            "Avg Satisfaction": kpis.get("avg_satisfaction", 0.0),
            "Avg Order Value (R$)": kpis.get("avg_order_value", 0.0),
        })

    st.divider()

    # ── Repeat purchase headline ─────────────────────────────────────────────
    if repeat_kpis:
        col1, col2, col3 = st.columns(3)
        col1.metric("Unique Customers",    f"{int(repeat_kpis.get('total_unique_customers', 0)):,}")
        col2.metric("One-Time Buyers",     f"{int(repeat_kpis.get('one_time_buyers', 0)):,}")
        col3.metric("Repeat Rate",         f"{repeat_kpis.get('repeat_rate_pct', 0.0):.1f}%",
                    delta=f"{repeat_kpis.get('avg_orders_per_customer', 0.0):.2f} avg orders")

    st.divider()

    # ── Insights ─────────────────────────────────────────────────────────────
    st.subheader("🔍 Automated Insights")
    StreamlitUtils.render_insight_box(
        cached_query(backend.insights, "generate_repeat_rate_insight")
    )
    StreamlitUtils.render_insight_box(
        cached_query(backend.insights, "generate_retention_insight")
    )
    StreamlitUtils.render_insight_box(
        cached_query(backend.insights, "generate_review_insight")
    )

except DatabaseError as e:
    st.error(f"⚠️ Data unavailable: {e}")
