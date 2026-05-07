from django.urls import path
from . import views

app_name = "payments"
urlpatterns = [
    path("record/", views.PaymentCreateView.as_view(), name="record_payment"),
    path("pay/", views.ClientPaymentView.as_view(), name="client_pay"),
    path("report/", views.ReportPaymentView.as_view(), name="report_payment"),
    path("notify/<int:pk>/", views.NotifyPaymentView.as_view(), name="notify_payment"),
    path("announce-due/", views.AnnouncePaymentDueView.as_view(), name="announce_due"),
    path("notification/<int:pk>/read/", views.MarkNotificationReadView.as_view(), name="mark_read"),
    path("notifications/read-all/", views.MarkAllNotificationsReadView.as_view(), name="mark_all_read"),
    path("handovers/", views.MoneyHandoverListView.as_view(), name="handover_list"),
    path("handovers/create/", views.MoneyHandoverCreateView.as_view(), name="create_handover"),
    path("handovers/<int:pk>/verify/", views.MoneyHandoverVerifyView.as_view(), name="verify_handover"),
    path("invoices/", views.CustomerInvoiceListView.as_view(), name="invoice_list"),
    path("invoices/unpaid/", views.UnpaidInvoiceListView.as_view(), name="unpaid_invoices"),
    path("expense/record/", views.ExpenseCreateView.as_view(), name="record_expense"),
]
