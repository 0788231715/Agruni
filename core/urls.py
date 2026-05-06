from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("notifications/mark-read/<int:pk>/", views.MarkNotificationReadView.as_view(), name="mark_notification_read"),
    path("notifications/mark-all-read/", views.MarkAllNotificationsReadView.as_view(), name="mark_all_notifications_read"),
]
