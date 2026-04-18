from django.urls import path
from .views import DashboardStatsView, PipelineSummaryView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('pipeline/', PipelineSummaryView.as_view(), name='dashboard-pipeline'),
]
