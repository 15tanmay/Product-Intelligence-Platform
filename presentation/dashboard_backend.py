from adapters.analytics_service import AnalyticsService
from use_cases.executive_kpis import ExecutiveKPIs
from use_cases.customer_analytics import CustomerAnalytics
from use_cases.retention_analytics import RetentionAnalytics
from use_cases.business_insights import BusinessInsights
from use_cases.segmentation import SegmentationAnalytics
from use_cases.revenue_analytics import RevenueAnalytics
from use_cases.cohort_analysis import CohortAnalytics
from use_cases.recommendation_engine import RecommendationEngine
from use_cases.payment_analytics import PaymentAnalytics
from use_cases.product_analytics import ProductAnalytics
from use_cases.seller_analytics import SellerAnalytics
from use_cases.geographic_analytics import GeographicAnalytics


class DashboardBackend:
    """Facade that provides all analytics use cases to the presentation layer."""

    def __init__(self) -> None:
        self.service = AnalyticsService()
        self.kpis = ExecutiveKPIs(self.service)
        self.customer = CustomerAnalytics(self.service)
        self.retention = RetentionAnalytics(self.service)
        self.insights = BusinessInsights(self.service)
        self.segmentation = SegmentationAnalytics(self.service)
        self.revenue = RevenueAnalytics(self.service)
        self.cohorts = CohortAnalytics(self.service)
        self.recommendations = RecommendationEngine(self.service)
        self.payments = PaymentAnalytics(self.service)
        self.products = ProductAnalytics(self.service)
        self.sellers = SellerAnalytics(self.service)
        self.geography = GeographicAnalytics(self.service)

    # ── convenience passthrough methods (used by cached_query) ──────────────
    def load_executive_summary(self) -> dict:
        return self.kpis.get_high_level_metrics()

    def load_customer_ratio(self):
        return self.customer.get_first_vs_repeat_ratio()

    def load_delivery_impact(self):
        return self.retention.analyze_delivery_impact()
