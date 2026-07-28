import streamlit as st

st.set_page_config(
    page_title="Product Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Product Intelligence Platform")
st.subheader("Customer Behaviour & Product Decision Support System")
st.markdown("---")

st.markdown("""
### Primary Business Question
> **"Why are first-time customers not becoming repeat customers?"**

Every dashboard, chart, and insight in this platform is designed to answer that question.

---

### Available Dashboards

| Dashboard | Description |
|-----------|-------------|
| 📋 **Executive Summary** | Core KPIs, repeat purchase rate, automated insights |
| 👥 **Customer Analytics** | First-time vs repeat ratio, cohort retention heatmap, RFM segmentation |
| 💰 **Revenue Analytics** | Monthly revenue trends, one-time vs repeat customer LTV |
| 🔄 **Retention Analytics** | Delivery impact, review score influence, time to second purchase |
| 🗂️ **Customer Segmentation** | RFM segments, recency vs monetary value scatter |
| 📦 **Product Analytics** | Category revenue, retention by category, price band analysis |
| 🎯 **Recommendation Center** | Products & categories driving repeat purchases |
| 🏥 **Business Health** | Data quality, table row counts, system status |
| 💳 **Payment Analytics** | Payment methods, installment behaviour vs retention |
| 🏪 **Seller Analytics** | Seller performance, seller quality impact on churn |
| 🗺️ **Geographic Analytics** | Retention by state, revenue by state, delivery delays |

---

### Dataset
**Olist Brazilian E-Commerce** — 99,441 orders across 9 relational tables, 2016–2018.
""")
