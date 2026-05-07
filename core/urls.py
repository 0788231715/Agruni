from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("projects/", views.ProjectsView.as_view(), name="projects"),
    path("services/", views.ServicesView.as_view(), name="services"),
    path("announcements/", views.AnnouncementListView.as_view(), name="announcement_list"),
    path("announcements/create/", views.AnnouncementCreateView.as_view(), name="announcement_create"),
    path("notifications/mark-read/<int:pk>/", views.MarkNotificationReadView.as_view(), name="mark_notification_read"),
    path("notifications/mark-all-read/", views.MarkAllNotificationsReadView.as_view(), name="mark_all_notifications_read"),
]
