from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import ServiceRequest, DriverAssignment, Pickup, Subscription, Vehicle, Zone

class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = "collection/vehicle_list.html"
    context_object_name = "vehicles"

class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    fields = ["plate_number", "model", "capacity_kg", "status"]
    template_name = "collection/vehicle_form.html"
    success_url = reverse_lazy("collection:vehicle_list")

    def form_valid(self, form):
        messages.success(self.request, f"Vehicle {form.cleaned_data['plate_number']} added to fleet.")
        return super().form_valid(form)
from .forms import ServiceRequestForm, SubscriptionForm

class ZoneListView(LoginRequiredMixin, ListView):
    model = Zone
    template_name = "collection/zone_list.html"
    context_object_name = "zones"

class ZoneCreateView(LoginRequiredMixin, CreateView):
    model = Zone
    fields = ["sector", "name", "manager", "collectors"]
    template_name = "collection/zone_form.html"
    success_url = reverse_lazy("collection:zone_list")

    def form_valid(self, form):
        messages.success(self.request, f"Zone {form.cleaned_data['name']} created successfully.")
        return super().form_valid(form)

class CollectorClientListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = "collection/collector_clients.html"
    context_object_name = "subscriptions"

    def get_queryset(self):
        return Subscription.objects.filter(collector=self.request.user, is_active=True).order_by('zone', 'customer__username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add payment info for each subscription
        for sub in context['subscriptions']:
            latest_invoice = sub.invoices.order_by('-created_at').first()
            sub.latest_invoice = latest_invoice
            if latest_invoice:
                sub.is_paid_online = latest_invoice.payments.filter(payment_method='ONLINE').exists()
            else:
                sub.is_paid_online = False
        return context

class ServiceRequestApproveView(LoginRequiredMixin, UpdateView):
    model = ServiceRequest
    fields = []
    template_name = "collection/request_confirm.html"
    success_url = reverse_lazy("dashboard:index")

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = ServiceRequest.RequestStatus.APPROVED
        obj.save()
        
        # Notify Customer
        Notification.objects.create(
            user=obj.customer,
            title="Request Approved",
            message=f"Your collection request #{obj.id} has been approved."
        )
        messages.success(request, "Request approved successfully.")
        return redirect(self.success_url)

class ServiceRequestRejectView(LoginRequiredMixin, UpdateView):
    model = ServiceRequest
    fields = []
    template_name = "collection/request_confirm.html"
    success_url = reverse_lazy("dashboard:index")

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = ServiceRequest.RequestStatus.CANCELLED
        obj.save()
        
        # Notify Customer
        Notification.objects.create(
            user=obj.customer,
            title="Request Rejected",
            message=f"Your collection request #{obj.id} has been rejected/cancelled."
        )
        messages.error(request, "Request rejected.")
        return redirect(self.success_url)

class SubscriptionCreateView(LoginRequiredMixin, CreateView):
    model = Subscription
    form_class = SubscriptionForm
    template_name = "collection/subscription_form.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        # Secretary usually registers for a customer
        messages.success(self.request, "Service agreement created successfully.")
        return super().form_valid(form)

class SubscriptionListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = "collection/subscription_list.html"
    context_object_name = "subscriptions"

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "GENERAL_MANAGER", "SECRETARY"]:
            return Subscription.objects.all().order_by('-created_at')
        return Subscription.objects.filter(customer=user).order_by('-created_at')

class SubscriptionDetailView(LoginRequiredMixin, DetailView):
    model = Subscription
    template_name = "collection/subscription_detail.html"
    context_object_name = "subscription"

class SubscriptionDownloadView(LoginRequiredMixin, DetailView):
    model = Subscription
    template_name = "collection/subscription_print.html"
    context_object_name = "subscription"

class ServiceRequestCreateView(LoginRequiredMixin, CreateView):
    model = ServiceRequest
    form_class = ServiceRequestForm
    template_name = "collection/request_form.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        form.instance.customer = self.request.user
        return super().form_valid(form)

class ServiceRequestListView(LoginRequiredMixin, ListView):
    model = ServiceRequest
    template_name = "collection/request_list.html"
    context_object_name = "requests"

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "GENERAL_MANAGER", "SUPERVISOR"]:
            return ServiceRequest.objects.all().order_by('-created_at')
        return ServiceRequest.objects.filter(customer=user).order_by('-created_at')

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
