from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardIndexView.as_view(), name="index"),
    path("finance/summary/", views.FinancialSummaryView.as_view(), name="financial_summary"),
    path("users/", views.UserManagementView.as_view(), name="user_management"),
    path("users/add/", views.UserCreateView.as_view(), name="user_create"),
]
