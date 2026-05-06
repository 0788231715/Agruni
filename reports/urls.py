from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("financial/pdf/", views.FinancialReportPDFView.as_view(), name="financial_report"),
]
