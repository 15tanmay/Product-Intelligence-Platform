"""Streamlit caching layer and backend singleton factory.

Separates the resource-initialisation concern from the page modules so that:
  - DashboardBackend is created once per Streamlit session (cache_resource).
  - Per-query results are cached for 1 hour (cache_data with TTL).

cached_query usage::

    df = cached_query(backend.products, "get_top_categories_by_revenue")
    kpis = cached_query(backend.kpis, "get_high_level_metrics")
"""
import streamlit as st

from presentation.dashboard_backend import DashboardBackend


@st.cache_resource
def get_backend() -> DashboardBackend:
    """Return a singleton DashboardBackend for the current Streamlit session."""
    return DashboardBackend()


@st.cache_data(ttl=3600, show_spinner=False)
def cached_query(_service_instance, method_name: str, *args, **kwargs):
    """Call *method_name* on *_service_instance* and cache the result for 1 hour.

    The leading underscore in *_service_instance* prevents Streamlit from
    hashing the object itself (which is not hashable), relying on *method_name*
    and *args* as the cache key instead.
    """
    method = getattr(_service_instance, method_name)
    return method(*args, **kwargs)
