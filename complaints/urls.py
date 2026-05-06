from django.urls import path
from . import views

app_name = "complaints"

urlpatterns = [
    path("list/", views.ComplaintListView.as_view(), name="complaint_list"),
    path("submit/", views.ComplaintCreateView.as_view(), name="complaint_submit"),
    path("resolve/<int:pk>/", views.ComplaintResolveView.as_view(), name="complaint_resolve"),
]
