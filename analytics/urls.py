# analytics/urls.py
from django.urls import path
from .views import analytics_series_json, AnalyticsPageView

app_name = 'analytics'
urlpatterns = [
    path("api/analytics.json", analytics_series_json, name="analytics_series_json"),
    path('analytics/', AnalyticsPageView.as_view(), name='analytics_page'),
]
