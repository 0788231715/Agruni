from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("register-user/", views.RegisterUserView.as_view(), name="register_user"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/toggle-active/", views.UserToggleActiveView.as_view(), name="user_toggle_active"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("request-registration/", views.RegistrationRequestView.as_view(), name="request_registration"),
    path("api/locations/", views.UserLocationsAPI.as_view(), name="user_locations_api"),
]
