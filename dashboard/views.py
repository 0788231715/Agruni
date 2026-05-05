from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import User
from collection.models import ServiceRequest, DriverAssignment, Vehicle, Pickup
from recycling.models import WasteSorting
from payments.models import Invoice, Payment
from complaints.models import Complaint
from django.db.models import Sum, Count

class DashboardIndexView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        role = request.user.role
        if role == User.Role.ADMIN or role == User.Role.MANAGER:
            return self.admin_dashboard(request)
        elif role == User.Role.CUSTOMER:
            return self.customer_dashboard(request)
        elif role == User.Role.DRIVER:
            return self.driver_dashboard(request)
        elif role == User.Role.SUPERVISOR:
            return self.supervisor_dashboard(request)
        elif role == User.Role.FINANCE:
            return self.finance_dashboard(request)
        elif role == User.Role.SORTING_STAFF:
            return self.recycling_dashboard(request)
        return redirect("core:home")

    def admin_dashboard(self, request):
        context = {
            "total_customers": User.objects.filter(role=User.Role.CUSTOMER).count(),
            "total_requests": ServiceRequest.objects.count(),
            "pending_requests": ServiceRequest.objects.filter(status=ServiceRequest.RequestStatus.PENDING).count(),
            "completed_pickups": Pickup.objects.count(),
            "total_vehicles": Vehicle.objects.count(),
            "total_revenue": Invoice.objects.filter(status=Invoice.InvoiceStatus.PAID).aggregate(Sum('amount'))['amount__sum'] or 0,
            "unpaid_invoices": Invoice.objects.filter(status=Invoice.InvoiceStatus.UNPAID).count(),
            "pending_complaints": Complaint.objects.filter(status=Complaint.ComplaintStatus.PENDING).count(),
        }
        return render(request, "dashboard/admin_dashboard.html", context)

    def customer_dashboard(self, request):
        context = {
            "my_requests": ServiceRequest.objects.filter(customer=request.user).order_by('-created_at')[:5],
            "my_invoices": Invoice.objects.filter(request__customer=request.user).order_by('-created_at')[:5],
            "my_complaints": Complaint.objects.filter(customer=request.user).order_by('-created_at')[:5],
        }
        return render(request, "dashboard/customer_dashboard.html", context)

    def driver_dashboard(self, request):
        context = {
            "assigned_pickups": DriverAssignment.objects.filter(driver=request.user, completed_at__isnull=True),
            "completed_count": DriverAssignment.objects.filter(driver=request.user, completed_at__isnull=False).count(),
        }
        return render(request, "dashboard/driver_dashboard.html", context)

    def supervisor_dashboard(self, request):
        context = {
            "pending_requests": ServiceRequest.objects.filter(status=ServiceRequest.RequestStatus.PENDING),
            "available_vehicles": Vehicle.objects.filter(status=Vehicle.VehicleStatus.AVAILABLE),
            "available_drivers": User.objects.filter(role=User.Role.DRIVER),
            "active_assignments": DriverAssignment.objects.filter(completed_at__isnull=True),
        }
        return render(request, "dashboard/supervisor_dashboard.html", context)

    def finance_dashboard(self, request):
        context = {
            "unpaid_invoices": Invoice.objects.filter(status=Invoice.InvoiceStatus.UNPAID),
            "recent_payments": Payment.objects.order_by('-payment_date')[:10],
            "total_revenue": Invoice.objects.filter(status=Invoice.InvoiceStatus.PAID).aggregate(Sum('amount'))['amount__sum'] or 0,
        }
        return render(request, "dashboard/finance_dashboard.html", context)

    def recycling_dashboard(self, request):
        context = {
            "pending_sortings": Pickup.objects.exclude(sortings__isnull=False),
            "recent_sortings": WasteSorting.objects.order_by('-sorting_date')[:10],
            "total_sorted_weight": WasteSorting.objects.aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0,
        }
        return render(request, "dashboard/recycling_dashboard.html", context)
