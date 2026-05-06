from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Complaint
from core.models import Notification

class ComplaintListView(LoginRequiredMixin, ListView):
    model = Complaint
    template_name = "complaints/complaint_list.html"
    context_object_name = "complaints"

    def get_queryset(self):
        user = self.request.user
        if user.role == "CUSTOMER":
            return Complaint.objects.filter(customer=user).order_by('-created_at')
        return Complaint.objects.all().order_by('-created_at')

class ComplaintCreateView(LoginRequiredMixin, CreateView):
    model = Complaint
    fields = ["subject", "description"]
    template_name = "complaints/complaint_form.html"
    success_url = reverse_lazy("complaints:complaint_list")

    def form_valid(self, form):
        form.instance.customer = self.request.user
        messages.success(self.request, "Your complaint has been submitted.")
        
        # Notify Admins
        from accounts.models import User
        admins = User.objects.filter(role="ADMIN")
        for admin in admins:
            Notification.objects.create(
                user=admin,
                title="New Complaint Submitted",
                message=f"Customer {self.request.user.username} submitted a complaint: {form.instance.subject}"
            )
        return super().form_valid(form)

class ComplaintResolveView(LoginRequiredMixin, UpdateView):
    model = Complaint
    fields = ["response", "status"]
    template_name = "complaints/complaint_resolve.html"
    success_url = reverse_lazy("complaints:complaint_list")

    def form_valid(self, form):
        messages.success(self.request, "Complaint status updated.")
        Notification.objects.create(
            user=self.object.customer,
            title="Complaint Update",
            message=f"Management has responded to your complaint: {self.object.subject}"
        )
        return super().form_valid(form)
