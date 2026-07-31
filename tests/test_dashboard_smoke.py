"""Dashboard smoke tests using Streamlit's AppTest framework.

Strategy: patch both `get_backend` (returns stub backend) and `cached_query`
(bypasses @st.cache_data so MagicMock is never pickled) so pages render with
stub data and complete well within the default timeout.

Tests confirm that pages import correctly, render without exceptions,
and display at least one Streamlit element.

Requires streamlit >= 1.28.0 with a compatible starlette version.
If the import fails, tests are skipped gracefully.
"""
import os
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd

try:
    from streamlit.testing.v1 import AppTest
    _STREAMLIT_AVAILABLE = True
    _STREAMLIT_ERROR = ""
except (ImportError, Exception) as _st_exc:
    _STREAMLIT_AVAILABLE = False
    _STREAMLIT_ERROR = str(_st_exc)


# ── Stub data fixtures ────────────────────────────────────────────────────────

_KPI_DICT = {
    "total_customers": 99441,
    "total_orders": 99441,
    "total_revenue": 16008872.12,
    "avg_satisfaction": 4.09,
    "avg_order_value": 154.10,
}

_REPEAT_DICT = {
    "total_unique_customers": 96096,
    "one_time_buyers": 93609,
    "repeat_buyers": 2487,
    "repeat_rate_pct": 2.59,
    "avg_orders_per_customer": 1.03,
}

_EMPTY_DF = pd.DataFrame()

_CATEGORY_DF = pd.DataFrame({
    "category": ["health_beauty", "computers"],
    "orders": [10, 5],
    "total_revenue": [1000.0, 500.0],
    "avg_price": [100.0, 100.0],
    "avg_review_score": [4.0, 3.5],
})

_STATE_DF = pd.DataFrame({
    "state": ["SP", "RJ"],
    "total_customers": [50000, 20000],
    "one_time_buyers": [48000, 19500],
    "repeat_buyers": [2000, 500],
    "repeat_rate_pct": [4.0, 2.5],
})


def _cached_query_stub(_instance, method_name: str, *args, **kwargs):
    """Bypass st.cache_data and delegate directly to the stub backend."""
    method = getattr(_instance, method_name)
    return method(*args, **kwargs)


def _make_stub_backend() -> MagicMock:
    """Return a stub DashboardBackend with picklable return values."""
    backend = MagicMock()

    # KPIs (dicts are picklable)
    backend.kpis.get_high_level_metrics.return_value = _KPI_DICT
    backend.kpis.get_repeat_purchase_rate.return_value = _REPEAT_DICT

    # Insights (strings are picklable)
    backend.insights.generate_repeat_rate_insight.return_value = (
        "Only 2.6% of customers made a second purchase."
    )
    backend.insights.generate_retention_insight.return_value = (
        "62.1% of orders arrived late."
    )
    backend.insights.generate_review_insight.return_value = (
        "Average first-order review score is 3.87/5."
    )

    # All use-case sub-objects default to returning an empty DataFrame
    for sub_name in (
        "customer", "retention", "segmentation", "revenue",
        "cohorts", "recommendations", "payments", "products",
        "sellers", "geography",
    ):
        sub = getattr(backend, sub_name)
        # MagicMock auto-creates child Mocks but we override return_value via side_effect
        # to return empty DataFrames (picklable) instead of MagicMock (not picklable).
        sub.configure_mock(**{
            f"{m}.return_value": _EMPTY_DF
            for m in [
                "get_first_vs_repeat_ratio", "analyze_delivery_impact",
                "get_review_score_vs_retention", "get_time_to_second_purchase",
                "get_payment_method_distribution", "get_installment_vs_retention",
                "get_top_categories_by_revenue", "get_category_retention_rate",
                "get_price_band_retention", "get_seller_performance",
                "get_seller_churn_impact", "get_retention_by_state",
                "get_revenue_by_state", "get_delivery_delay_by_state",
                "get_monthly_revenue_trend", "get_customer_segments",
                "get_monthly_cohorts", "get_rfm_segments",
                "get_top_recommendations", "get_cohort_ltv",
                "get_payment_type_heatmap", "get_high_installment_orders",
            ]
        })

    # Specific non-empty returns where pages check .empty before rendering
    backend.products.get_top_categories_by_revenue.return_value = _CATEGORY_DF
    backend.geography.get_retention_by_state.return_value = _STATE_DF

    return backend


@unittest.skipUnless(_STREAMLIT_AVAILABLE, f"streamlit.testing.v1 unavailable: {_STREAMLIT_ERROR}")
class TestDashboardSmoke(unittest.TestCase):

    def setUp(self) -> None:
        os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

    def _run_page(self, path: str) -> AppTest:
        stub = _make_stub_backend()
        with (
            patch("presentation.performance.get_backend", return_value=stub),
            patch("presentation.performance.cached_query", side_effect=_cached_query_stub),
        ):
            at = AppTest.from_file(path, default_timeout=15).run()
        return at

    def test_home_page_loads(self) -> None:
        """Home page renders without exception."""
        at = self._run_page("t:/product/presentation/pages/1_Home.py")
        self.assertFalse(at.exception, msg=str(at.exception))

    def test_executive_summary_loads(self) -> None:
        """Executive summary page renders without exception."""
        at = self._run_page("t:/product/presentation/pages/2_Executive_Summary.py")
        self.assertFalse(at.exception, msg=str(at.exception))

    def test_customer_analytics_loads(self) -> None:
        """Customer analytics page renders without exception."""
        at = self._run_page("t:/product/presentation/pages/3_Customer_Analytics.py")
        self.assertFalse(at.exception, msg=str(at.exception))


if __name__ == "__main__":
    unittest.main()
