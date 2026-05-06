from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import ServiceRequest, DriverAssignment, Pickup, Subscription
from .forms import ServiceRequestForm, SubscriptionForm

class SubscriptionCreateView(LoginRequiredMixin, CreateView):
    model = Subscription
    form_class = SubscriptionForm
    template_name = "collection/subscription_form.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        # Secretary usually registers for a customer
        return super().form_valid(form)

class ServiceRequestCreateView(LoginRequiredMixin, CreateView):
    model = ServiceRequest
    form_class = ServiceRequestForm
    template_name = "collection/request_form.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        form.instance.customer = self.request.user
        return super().form_valid(form)

class ServiceRequestDetailView(LoginRequiredMixin, DetailView):
    model = ServiceRequest
    template_name = "collection/request_detail.html"
    context_object_name = "request_obj"

class DriverAssignmentListView(LoginRequiredMixin, ListView):
    model = DriverAssignment
    template_name = "collection/assignment_list.html"
    context_object_name = "assignments"

    def get_queryset(self):
        return DriverAssignment.objects.filter(driver=self.request.user, completed_at__isnull=True)

class PickupUpdateView(LoginRequiredMixin, UpdateView):
    model = Pickup
    fields = ["actual_weight_kg", "proof_image", "notes"]
    template_name = "collection/pickup_form.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        # Update assignment and request status
        pickup = form.save()
        assignment = pickup.assignment
        assignment.completed_at = pickup.pickup_time
        assignment.save()
        
        request_obj = assignment.request
        request_obj.status = ServiceRequest.RequestStatus.COMPLETED
        request_obj.save()
        
        return super().form_valid(form)
