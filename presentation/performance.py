import streamlit as st
from presentation.dashboard_backend import DashboardBackend

@st.cache_resource
def get_backend():
    return DashboardBackend()

@st.cache_data(ttl=3600)
def cached_query(_instance, method_name, *args, **kwargs):
    method = getattr(_instance, method_name)
    return method(*args, **kwargs)
