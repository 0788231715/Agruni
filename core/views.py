from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Notification, Announcement
from accounts.models import User
from collection.models import Subscription

class AnnouncementCreateView(LoginRequiredMixin, CreateView):
    model = Announcement
    fields = ["title", "message"]
    template_name = "core/announcement_form.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        form.instance.sender = self.request.user
        announcement = form.save()
        messages.success(self.request, "Announcement broadcasted successfully.")
        
        # Determine target audience: If sender is COLLECTOR, notify their clients.
        # If ADMIN/GM, notify everyone? User specified "collect announce time to pay to all his client"
        if self.request.user.role == User.Role.COLLECTOR:
            # Find all active clients assigned to this collector
            clients = Subscription.objects.filter(
                collector=self.request.user, 
                is_active=True
            ).values_list('customer', flat=True).distinct()
            
            for client_id in clients:
                Notification.objects.create(
                    user_id=client_id,
                    title=f"Important Announcement: {announcement.title}",
                    message=f"From your Collector {self.request.user.username}: {announcement.message}"
                )
        return super().form_valid(form)

class AnnouncementListView(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = "core/announcement_list.html"
    context_object_name = "announcements"

    def get_queryset(self):
        if self.request.user.role == User.Role.CUSTOMER:
            # Customers see announcements from their collectors
            sub = Subscription.objects.filter(customer=self.request.user, is_active=True).first()
            if sub and sub.collector:
                return Announcement.objects.filter(sender=sub.collector).order_by('-created_at')
            return Announcement.objects.none()
        return Announcement.objects.all().order_by('-created_at')

class HomeView(TemplateView):
    template_name = "core/home.html"

class AboutView(TemplateView):
    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import User
        context['staff_members'] = User.objects.filter(
            role__in=[User.Role.ADMIN, User.Role.GENERAL_MANAGER, User.Role.SECRETARY, User.Role.FINANCE],
            is_verified=True
        ).order_by('role')
        return context

class ContactView(TemplateView):
    template_name = "core/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import User
        # Fetch only verified management staff to show on contact page
        context['staff_members'] = User.objects.filter(
            role__in=[User.Role.ADMIN, User.Role.GENERAL_MANAGER, User.Role.SECRETARY, User.Role.FINANCE],
            is_verified=True
        ).order_by('role')
        return context

class ProjectsView(TemplateView):
    template_name = "core/projects.html"

class ServicesView(TemplateView):
    template_name = "core/services.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from services.models import Service
        context['services'] = Service.objects.filter(is_active=True)
        return context

class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({"status": "success"})

class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"status": "success"})
