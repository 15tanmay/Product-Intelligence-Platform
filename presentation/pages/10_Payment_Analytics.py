import streamlit as st
from presentation.performance import get_backend, cached_query
from adapters.plotly_service import PlotlyService
from adapters.analytics_service import DatabaseError

st.title("💳 Payment Analytics")
st.caption("Payment method distribution and installment behaviour vs customer retention.")

backend = get_backend()

try:
    # ── Payment method distribution ───────────────────────────────────────────
    st.subheader("Payment Method Distribution")
    df_pay = cached_query(backend.payments, "get_payment_method_distribution")
    if not df_pay.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = PlotlyService.create_pie_chart(
                df_pay, names="payment_type", values="order_count",
                title="Orders by Payment Method",
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = PlotlyService.create_bar_chart(
                df_pay, x="payment_type", y="avg_order_value",
                title="Average Order Value (R$) by Payment Method",
                text="avg_order_value",
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Installments vs retention ─────────────────────────────────────────────
    st.subheader("Installment Count vs Customer Retention")
    df_inst = cached_query(backend.payments, "get_installment_vs_retention")
    if not df_inst.empty:
        fig3 = PlotlyService.create_grouped_bar(
            df_inst, x="installment_band", y="customers",
            color="customer_type",
            title="One-Time vs Repeat Buyers by Number of Installments",
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.info(
            "💡 Customers paying in more installments may face financial constraints that "
            "reduce likelihood of repeat purchasing.",
            icon="💡",
        )

except DatabaseError as e:
    st.error(f"⚠️ Data unavailable: {e}")
