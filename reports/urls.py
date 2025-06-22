from django.urls import path
from .views import ReportCreateView

urlpatterns = [
    path('', ReportCreateView.as_view(), name='report-create')
    # path('<uuid:pk>/', ReportDetailView.as_view(), name='report-detail'),
    # path('<uuid:pk>/download/', ReportDownloadView.as_view(), name='report-download'),
]