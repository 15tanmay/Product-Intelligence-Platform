import streamlit as st

class StreamlitUtils:
    @staticmethod
    def setup_page(title: str, layout: str = "wide"):
        st.set_page_config(page_title=title, layout=layout)
        st.title(title)

    @staticmethod
    def display_kpi_row(metrics: dict):
        cols = st.columns(len(metrics))
        for col, (label, value) in zip(cols, metrics.items()):
            if isinstance(value, float):
                col.metric(label=label.replace('_', ' ').title(), value=f"{value:,.2f}")
            else:
                col.metric(label=label.replace('_', ' ').title(), value=f"{value:,}")

    @staticmethod
    def render_insight_box(insight_text: str):
        st.info(insight_text, icon="💡")
