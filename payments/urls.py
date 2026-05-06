from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("record/", views.PaymentCreateView.as_view(), name="record_payment"),
    path("handovers/", views.MoneyHandoverListView.as_view(), name="handover_list"),
    path("handovers/create/", views.MoneyHandoverCreateView.as_view(), name="create_handover"),
    path("handovers/<int:pk>/verify/", views.MoneyHandoverVerifyView.as_view(), name="verify_handover"),
    path("invoices/unpaid/", views.UnpaidInvoiceListView.as_view(), name="unpaid_invoices"),
    path("expense/record/", views.ExpenseCreateView.as_view(), name="record_expense"),
]
