import streamlit as st

def apply_theme():
    st.markdown("""
        <style>
        .stApp {
            background-color: #FAFAFA;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
