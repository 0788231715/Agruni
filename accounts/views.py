from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count
from django.contrib import messages
from .forms import (
    DashboardUserRegistrationForm, UserRegistrationForm, UserUpdateForm, 
    ProfileUpdateForm, RegistrationRequestForm, ProfilePictureUpdateForm,
    LimitedUserUpdateForm
)
from .models import User, Profile, RegistrationRequest, ProfileUpdateRequest

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

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/profile.html"
    context_object_name = "profile_user"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if user has an APPROVED request that is not yet COMPLETED
        context["approved_request"] = ProfileUpdateRequest.objects.filter(
            user=self.request.user, 
            status=ProfileUpdateRequest.Status.APPROVED
        ).first()
        return context

class ActualProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = LimitedUserUpdateForm
    template_name = "accounts/edit_profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        # Only allow if an APPROVED request exists
        if not ProfileUpdateRequest.objects.filter(user=request.user, status=ProfileUpdateRequest.Status.APPROVED).exists():
            messages.error(request, "You do not have an approved profile update session.")
            return redirect("accounts:profile")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        # Save changes
        response = super().form_valid(form)
        
        # Mark request as COMPLETED
        req = ProfileUpdateRequest.objects.filter(
            user=self.request.user, 
            status=ProfileUpdateRequest.Status.APPROVED
        ).first()
        if req:
            req.status = ProfileUpdateRequest.Status.COMPLETED
            req.save()
            
            # Notify Admin that user has finished update
            admin_user = User.objects.filter(role=User.Role.ADMIN, is_active=True).first()
            if not admin_user:
                admin_user = User.objects.filter(is_staff=True, is_active=True).first()
            
            if admin_user:
                from tasks.models import Task
                Task.objects.create(
                    creator=self.request.user,
                    assignee=admin_user,
                    title=f"Update Finished: {self.request.user.username}",
                    description=f"User {self.request.user.username} has finished updating their profile following your approval.",
                    status=Task.TaskStatus.COMPLETED
                )
        
        messages.success(self.request, "Profile updated successfully. Your edit session is now closed.")
        return response

class UserToggleActiveView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role in ["ADMIN", "GENERAL_MANAGER"]

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        status = "enabled" if user.is_active else "disabled"
        messages.success(request, f"User {user.username} has been {status}.")
        return redirect("accounts:user_list")

class ProfilePictureUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfilePictureUpdateForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile picture updated successfully.")
        return super().form_valid(form)

class RequestProfileUpdateView(LoginRequiredMixin, View):
    def post(self, request):
        details = request.POST.get("details")
        if not details:
            messages.error(request, "Please provide the details of your requested changes.")
            return redirect("accounts:profile")
        
        # Create the formal request
        ProfileUpdateRequest.objects.create(
            user=request.user,
            requested_changes=details,
            status=ProfileUpdateRequest.Status.PENDING
        )
        
        # Also create a task for the Admin to notify them
        admin_user = User.objects.filter(role=User.Role.ADMIN, is_active=True).first()
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True, is_active=True).first()
        
        if admin_user:
            from tasks.models import Task
            Task.objects.create(
                creator=request.user,
                assignee=admin_user,
                title=f"New Profile Update Request: {request.user.username}",
                description=f"User {request.user.username} has submitted a new profile update request. Please review it in the Management section.\n\nDetails: {details}",
                status=Task.TaskStatus.PENDING
            )
            
        messages.success(request, "Your change request has been sent for review. An administrator will process it soon.")
        return redirect("accounts:profile")

class ProfileUpdateRequestListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ProfileUpdateRequest
    template_name = "accounts/profile_request_list.html"
    context_object_name = "requests"
    
    def get_queryset(self):
        return ProfileUpdateRequest.objects.all().order_by('-created_at')

class HandleProfileUpdateRequestView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        req = get_object_or_404(ProfileUpdateRequest, pk=pk)
        action = request.POST.get("action")
        admin_notes = request.POST.get("admin_notes", "")
        
        if action == "approve":
            req.status = ProfileUpdateRequest.Status.APPROVED
            messages.success(request, f"Request from {req.user.username} has been approved.")
            # Note: Automatic applying of changes is tricky with free-form text.
            # Usually admin would manually apply them. 
        elif action == "reject":
            req.status = ProfileUpdateRequest.Status.REJECTED
            messages.success(request, f"Request from {req.user.username} has been rejected.")
            
        req.admin_notes = admin_notes
        req.save()
        
        # Notify the user
        from core.models import Notification
        Notification.objects.create(
            user=req.user,
            title="Profile Update Status",
            message=f"Your profile update request has been {req.status.lower()}. {f'Notes: {admin_notes}' if admin_notes else ''}",
            link=reverse_lazy("accounts:profile")
        )
        
        return redirect("accounts:profile_request_list")
