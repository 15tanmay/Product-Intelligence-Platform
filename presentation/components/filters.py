import streamlit as st

def date_range_filter():
    st.sidebar.subheader("Global Filters")
    return st.sidebar.date_input("Date Range", [])
