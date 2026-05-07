from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Payment, Invoice, MoneyHandover, Expense
from .forms import PaymentForm, MoneyHandoverForm, ExpenseForm, ClientPaymentForm
from django.utils import timezone
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from core.models import Notification

User = get_user_model()

from django.db.models import Q, Sum

class MoneyHandoverListView(LoginRequiredMixin, ListView):
    model = MoneyHandover
    template_name = "payments/handover_list.html"
    context_object_name = "handovers"

    def get_queryset(self):
        user = self.request.user
        if user.role == "ADMIN" or user.role == "GENERAL_MANAGER":
            return MoneyHandover.objects.all().order_by('-created_at')
        
        # Location Managers see handovers to them OR in their zones
        from collection.models import Zone
        managed_zones = Zone.objects.filter(manager=user)
        return MoneyHandover.objects.filter(
            Q(to_user=user) | Q(zone__in=managed_zones)
        ).order_by('-created_at')

class UnpaidInvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "payments/unpaid_list.html"
    context_object_name = "invoices"

    def get_queryset(self):
        user = self.request.user
        queryset = Invoice.objects.filter(status=Invoice.InvoiceStatus.UNPAID).order_by('due_date')
        
        if user.role == "ADMIN" or user.role == "GENERAL_MANAGER" or user.role == "FINANCE":
            return queryset
        
        # Location Managers see unpaid clients in their zones
        from collection.models import Zone
        managed_zones = Zone.objects.filter(manager=user)
        return queryset.filter(subscription__zone__in=managed_zones)

class CustomerInvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "payments/invoice_list.html"
    context_object_name = "invoices"

    def get_queryset(self):
        return Invoice.objects.filter(subscription__customer=self.request.user).order_by('-created_at')

class ClientPaymentView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = ClientPaymentForm
    template_name = "payments/client_payment.html"
    success_url = reverse_lazy("dashboard:index")

    def get_initial(self):
        invoice = get_object_or_404(Invoice, id=self.request.GET.get('invoice'), subscription__customer=self.request.user)
        return {'amount': invoice.amount, 'invoice': invoice}

    def form_valid(self, form):
        invoice = get_object_or_404(Invoice, id=self.request.GET.get('invoice'))
        form.instance.invoice = invoice
        form.instance.collected_by = None # Online payment
        response = super().form_valid(form)
        
        # Update Invoice
        invoice.status = Invoice.InvoiceStatus.PAID
        invoice.save()

        # Notify Management
        targets = User.objects.filter(role__in=["ADMIN", "FINANCE"])
        for target in targets:
            Notification.objects.create(
                user=target,
                title="Online Payment Received",
                message=f"Customer {self.request.user.username} paid RWF {form.instance.amount} online."
            )
        
        Notification.objects.create(
            user=self.request.user,
            title="Payment Successful",
            message=f"Your payment of RWF {form.instance.amount} has been received."
        )
        return response

class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        note = get_object_or_404(Notification, id=pk, user=request.user)
        note.is_read = True
        note.save()
        return JsonResponse({"status": "success"})

class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"status": "success"})

class AnnouncePaymentDueView(LoginRequiredMixin, View):
    def post(self, request):
        if request.user.role not in ["ADMIN", "LOCATION_MANAGER", "FINANCE"]:
            return redirect("dashboard:index")
        
        # Simple logic to notify all customers with unpaid invoices
        unpaid_invoices = Invoice.objects.filter(status=Invoice.InvoiceStatus.UNPAID)
        for inv in unpaid_invoices:
            Notification.objects.create(
                user=inv.subscription.customer,
                title="Payment Due Reminder",
                message=f"Friendly reminder: Your invoice #{inv.invoice_number} for RWF {inv.amount} is due on {inv.due_date}."
            )
        messages.success(request, "Payment reminders sent to all unpaid clients.")
        return redirect("dashboard:index")

class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = "payments/payment_form.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        form.instance.collected_by = self.request.user
        response = super().form_valid(form)
        # Update invoice status
        invoice = form.instance.invoice
        invoice.status = Invoice.InvoiceStatus.PAID
        invoice.save()
        return response

class MoneyHandoverCreateView(LoginRequiredMixin, CreateView):
    model = MoneyHandover
    form_class = MoneyHandoverForm
    template_name = "payments/handover_form.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        # Logic to auto-assign payments could be added here
        return super().form_valid(form)

class MoneyHandoverVerifyView(LoginRequiredMixin, UpdateView):
    model = MoneyHandover
    fields = ["status", "notes"]
    template_name = "payments/handover_verify.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        if form.instance.status == MoneyHandover.HandoverStatus.RECEIVED:
            form.instance.verified_at = timezone.now()
        return super().form_valid(form)

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "payments/expense_form.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        return super().form_valid(form)
