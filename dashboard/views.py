from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from accounts.models import User
from collection.models import ServiceRequest, DriverAssignment, Vehicle, Pickup, Subscription, Zone
from recycling.models import WasteSorting
from payments.models import Invoice, Payment, Expense, MoneyHandover, SalaryOrCommission
from complaints.models import Complaint
from django.db.models import Sum, Count
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import DashboardUserCreationForm

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in [User.Role.ADMIN, User.Role.GENERAL_MANAGER, User.Role.SECRETARY]

class UserCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = User
    form_class = DashboardUserCreationForm
    template_name = "dashboard/user_form.html"
    success_url = reverse_lazy("dashboard:user_management")

    def form_valid(self, form):
        messages.success(self.request, f"User {form.cleaned_data['username']} created successfully.")
        return super().form_valid(form)

class UserManagementView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = User
    template_name = "dashboard/user_management.html"
    context_object_name = "users"

    def get_queryset(self):
        queryset = User.objects.all().order_by('role', 'username')
        role_filter = self.request.GET.get('role')
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["roles"] = User.Role.choices
        return context

class FinancialSummaryView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "dashboard/financial_summary.html"
    context_object_name = "invoices"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_revenue"] = Invoice.objects.filter(status=Invoice.InvoiceStatus.PAID).aggregate(Sum('amount'))['amount__sum'] or 0
        context["pending_revenue"] = Invoice.objects.filter(status=Invoice.InvoiceStatus.UNPAID).aggregate(Sum('amount'))['amount__sum'] or 0
        context["expenses"] = Expense.objects.order_by('-date')[:10]
        context["total_expenses"] = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        return context

class DashboardIndexView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        role = request.user.role
        if role == User.Role.ADMIN:
            return self.admin_dashboard(request)
        elif role == User.Role.SECRETARY:
            return self.secretary_dashboard(request)
        elif role == User.Role.GENERAL_MANAGER:
            return self.general_manager_dashboard(request)
        elif role == User.Role.LOCATION_MANAGER:
            return self.location_manager_dashboard(request)
        elif role == User.Role.FINANCE:
            return self.finance_dashboard(request)
        elif role == User.Role.SUPERVISOR:
            return self.supervisor_dashboard(request)
        elif role == User.Role.COLLECTOR:
            return self.collector_dashboard(request)
        elif role == User.Role.DRIVER:
            return self.driver_dashboard(request)
        elif role == User.Role.CUSTOMER:
            return self.customer_dashboard(request)
        elif role == User.Role.SORTING_STAFF:
            return self.recycling_dashboard(request)
        return redirect("core:home")

    def admin_dashboard(self, request):
        total_revenue = Invoice.objects.filter(status=Invoice.InvoiceStatus.PAID).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Monthly Revenue Data for Chart
        from django.db.models.functions import TruncMonth
        monthly_revenue = Invoice.objects.filter(status=Invoice.InvoiceStatus.PAID) \
            .annotate(month=TruncMonth('created_at')) \
            .values('month') \
            .annotate(total=Sum('amount')) \
            .order_by('month')

        chart_labels = [item['month'].strftime("%b %Y") for item in monthly_revenue]
        chart_data = [float(item['total']) for item in monthly_revenue]

        context = {
            "total_customers": User.objects.filter(role=User.Role.CUSTOMER).count(),
            "paid_clients": Invoice.objects.filter(status=Invoice.InvoiceStatus.PAID).values('subscription__customer').distinct().count(),
            "unpaid_clients": Invoice.objects.filter(status=Invoice.InvoiceStatus.UNPAID).values('subscription__customer').distinct().count(),
            "active_collectors": User.objects.filter(role=User.Role.COLLECTOR, is_active=True).count(),
            "active_drivers": User.objects.filter(role=User.Role.DRIVER, is_active=True).count(),
            "total_staff": User.objects.exclude(role=User.Role.CUSTOMER).count(),
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_profit": total_revenue - total_expenses,
            "pending_handovers": MoneyHandover.objects.filter(status=MoneyHandover.HandoverStatus.PENDING).count(),
            "pending_complaints": Complaint.objects.filter(status=Complaint.ComplaintStatus.PENDING).count(),
            "active_subscriptions": Subscription.objects.filter(is_active=True).count(),
            "chart_labels": chart_labels,
            "chart_data": chart_data,
        }
        return render(request, "dashboard/admin_dashboard.html", context)

    def secretary_dashboard(self, request):
        context = {
            "recent_customers": User.objects.filter(role=User.Role.CUSTOMER).order_by('-date_joined')[:10],
            "active_subscriptions": Subscription.objects.filter(is_active=True).count(),
            "recent_requests": ServiceRequest.objects.order_by('-created_at')[:10],
        }
        return render(request, "dashboard/secretary_dashboard.html", context)

    def general_manager_dashboard(self, request):
        context = {
            "total_locations": Zone.objects.count(),
            "location_managers": User.objects.filter(role=User.Role.LOCATION_MANAGER).count(),
            "total_collections": Pickup.objects.count(),
            "recent_handovers": MoneyHandover.objects.order_by('-created_at')[:10],
        }
        return render(request, "dashboard/general_manager_dashboard.html", context)

    def location_manager_dashboard(self, request):
        # Filter data by managed zones
        managed_zones = Zone.objects.filter(manager=request.user)
        context = {
            "managed_zones": managed_zones,
            "collectors": User.objects.filter(role=User.Role.COLLECTOR, assigned_requests__zone__in=managed_zones).distinct(),
            "pending_handovers": MoneyHandover.objects.filter(to_user=request.user, status=MoneyHandover.HandoverStatus.PENDING),
            "unpaid_invoices": Invoice.objects.filter(subscription__zone__in=managed_zones, status=Invoice.InvoiceStatus.UNPAID),
        }
        return render(request, "dashboard/location_manager_dashboard.html", context)

    def collector_dashboard(self, request):
        context = {
            "assigned_customers": Subscription.objects.filter(collector=request.user, is_active=True),
            "assigned_requests": ServiceRequest.objects.filter(collector=request.user, status=ServiceRequest.RequestStatus.ASSIGNED),
            "my_earnings": SalaryOrCommission.objects.filter(employee=request.user).order_by('-period_end')[:5],
            "pending_handovers": MoneyHandover.objects.filter(from_user=request.user, status=MoneyHandover.HandoverStatus.PENDING),
        }
        return render(request, "dashboard/collector_dashboard.html", context)

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
        # Data for Charts
        waste_by_category = WasteSorting.objects.values('category__name').annotate(total_weight=Sum('weight_kg'))
        cat_labels = [item['category__name'] for item in waste_by_category]
        cat_data = [float(item['total_weight']) for item in waste_by_category]

        total_recycled = RecyclingRecord.objects.aggregate(Sum('output_weight_kg'))['output_weight_kg__sum'] or 0
        total_disposed = DisposalRecord.objects.count() # Simplified, maybe weight is better but Disposal doesn't have it?
        # Let's check if DisposalRecord should have weight. It doesn't in models.py. 
        # It links to WasteSorting, so we can get weight from there.
        total_disposed_weight = DisposalRecord.objects.aggregate(Sum('sorting__weight_kg'))['sorting__weight_kg__sum'] or 0
        
        total_sorted = WasteSorting.objects.aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0
        recycled_pc = (float(total_recycled) / float(total_sorted) * 100) if total_sorted else 0
        disposed_pc = (float(total_disposed_weight) / float(total_sorted) * 100) if total_sorted else 0

        context = {
            "pending_sortings": Pickup.objects.exclude(sortings__isnull=False),
            "recent_sortings": WasteSorting.objects.order_by('-sorting_date')[:10],
            "total_sorted_weight": total_sorted,
            "total_recycled_weight": total_recycled,
            "total_disposed_weight": total_disposed_weight,
            "recycled_pc": recycled_pc,
            "disposed_pc": disposed_pc,
            "cat_labels": cat_labels,
            "cat_data": cat_data,
        }
        return render(request, "dashboard/recycling_dashboard.html", context)
