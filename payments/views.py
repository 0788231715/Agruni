from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Payment, Invoice, MoneyHandover, Expense
from .forms import PaymentForm, MoneyHandoverForm, ExpenseForm
from django.utils import timezone

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
