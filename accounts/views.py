from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.contrib import messages
from .forms import DashboardUserRegistrationForm, UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, RegistrationRequestForm
from .models import User, Profile, RegistrationRequest

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        allowed_roles = [User.Role.ADMIN, User.Role.GENERAL_MANAGER, User.Role.SECRETARY]
        return self.request.user.role in allowed_roles

    def handle_no_permission(self):
        messages.error(self.request, "Access denied. Only management staff can access this page.")
        return redirect("dashboard:index")

class RegisterUserView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = User
    form_class = DashboardUserRegistrationForm
    template_name = "accounts/register_user.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"User {self.object.username} registered successfully.")
        return response

class UserListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all().order_by('-date_joined')
        
        # Region-Locked Filtering for Location Managers
        if user.role == User.Role.LOCATION_MANAGER:
            from collection.models import Zone, Subscription
            managed_zones = Zone.objects.filter(manager=user)
            
            # Collectors in managed zones (via Subscriptions)
            collectors_in_zone = Subscription.objects.filter(zone__in=managed_zones).values_list('collector', flat=True)
            # Customers in managed zones
            customers_in_zone = Subscription.objects.filter(zone__in=managed_zones).values_list('customer', flat=True)
            
            queryset = queryset.filter(
                Q(id__in=collectors_in_zone) | Q(id__in=customers_in_zone)
            )

        # Search
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(username__icontains=q) | 
                Q(first_name__icontains=q) | 
                Q(last_name__icontains=q) | 
                Q(email__icontains=q)
            )

        # Filters
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        active = self.request.GET.get('active')
        if active == '1':
            queryset = queryset.filter(is_active=True)
        elif active == '0':
            queryset = queryset.filter(is_active=False)

        verified = self.request.GET.get('verified')
        if verified == '1':
            queryset = queryset.filter(is_verified=True)
        elif verified == '0':
            queryset = queryset.filter(is_verified=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        all_users = self.get_queryset() # Use filtered queryset for counts if Location Manager
        
        context['total_count'] = all_users.count()
        context['active_count'] = all_users.filter(is_active=True).count()
        context['customer_count'] = all_users.filter(role=User.Role.CUSTOMER).count()
        context['staff_count'] = all_users.exclude(role=User.Role.CUSTOMER).count()
        context['roles'] = User.Role.choices
        return context

class RegistrationRequestView(CreateView):
    model = RegistrationRequest
    form_class = RegistrationRequestForm
    template_name = "accounts/registration_request.html"
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, "Your registration request has been submitted. Our team will contact you shortly.")
        return super().form_valid(form)

class UserLocationsAPI(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        users = User.objects.filter(latitude__isnull=False, longitude__isnull=False).values(
            'username', 'first_name', 'last_name', 'role', 'latitude', 'longitude'
        )
        # Professional color scheme for all 10 roles
        ROLE_COLORS = {
            User.Role.ADMIN: '#6f42c1',            # Purple
            User.Role.SECRETARY: '#e83e8c',        # Pink
            User.Role.GENERAL_MANAGER: '#1b4332',  # Dark Green
            User.Role.LOCATION_MANAGER: '#dc3545', # Red
            User.Role.FINANCE: '#0dcaf0',          # Cyan
            User.Role.SUPERVISOR: '#ffc107',       # Yellow
            User.Role.COLLECTOR: '#198754',        # Green
            User.Role.DRIVER: '#fd7e14',           # Orange
            User.Role.CUSTOMER: '#0d6efd',         # Blue
            User.Role.SORTING_STAFF: '#20c997',    # Teal
        }

        results = []
        for u in users:
            role_display = dict(User.Role.choices).get(u['role'], u['role'])
            color = ROLE_COLORS.get(u['role'], '#6c757d') # Default grey
            
            results.append({
                'name': f"{u['first_name']} {u['last_name']}".strip() or u['username'],
                'username': u['username'],
                'role': role_display,
                'lat': float(u['latitude']),
                'lng': float(u['longitude']),
                'color': color
            })
        return JsonResponse(results, safe=False)

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, "profile"):
            context["profile_form"] = ProfileUpdateForm(instance=self.request.user.profile)
        else:
            context["profile_form"] = ProfileUpdateForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_form = UserUpdateForm(request.POST, request.FILES, instance=self.object)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=self.object.profile if hasattr(self.object, "profile") else None)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = self.object
            profile.save()
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=user_form, profile_form=profile_form))
