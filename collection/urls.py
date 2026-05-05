from django.urls import path
from . import views

app_name = "collection"

urlpatterns = [
    path("request/create/", views.ServiceRequestCreateView.as_view(), name="request_create"),
    path("request/<int:pk>/", views.ServiceRequestDetailView.as_view(), name="request_detail"),
    path("assignments/", views.DriverAssignmentListView.as_view(), name="assignment_list"),
    path("pickup/<int:pk>/update/", views.PickupUpdateView.as_view(), name="pickup_update"),
]
