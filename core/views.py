from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Notification

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
