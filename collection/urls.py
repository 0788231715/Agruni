from django.urls import path
from . import views

app_name = "collection"

urlpatterns = [
    path("request/create/", views.ServiceRequestCreateView.as_view(), name="request_create"),
    path("request/<int:pk>/", views.ServiceRequestDetailView.as_view(), name="request_detail"),
    path("request/<int:pk>/approve/", views.ServiceRequestApproveView.as_view(), name="request_approve"),
    path("request/<int:pk>/reject/", views.ServiceRequestRejectView.as_view(), name="request_reject"),
    path("zones/", views.ZoneListView.as_view(), name="zone_list"),
    path("zones/add/", views.ZoneCreateView.as_view(), name="zone_add"),
    path("subscriptions/", views.SubscriptionListView.as_view(), name="subscription_list"),
    path("subscriptions/create/", views.SubscriptionCreateView.as_view(), name="subscription_create"),
    path("subscriptions/<int:pk>/", views.SubscriptionDetailView.as_view(), name="subscription_detail"),
    path("subscriptions/<int:pk>/download/", views.SubscriptionDownloadView.as_view(), name="subscription_download"),
    path("my-clients/", views.CollectorClientListView.as_view(), name="my_clients"),
    path("assignments/", views.DriverAssignmentListView.as_view(), name="assignment_list"),
    path("vehicles/", views.VehicleListView.as_view(), name="vehicle_list"),
    path("vehicles/add/", views.VehicleCreateView.as_view(), name="vehicle_add"),
    path("pickup/<int:pk>/update/", views.PickupUpdateView.as_view(), name="pickup_update"),
]
