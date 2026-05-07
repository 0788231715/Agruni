from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("register-user/", views.RegisterUserView.as_view(), name="register_user"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/toggle-active/", views.UserToggleActiveView.as_view(), name="user_toggle_active"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ActualProfileUpdateView.as_view(), name="profile_edit"),
    path("profile/picture/", views.ProfilePictureUpdateView.as_view(), name="profile_picture_update"),
    path("profile/request-update/", views.RequestProfileUpdateView.as_view(), name="request_profile_update"),
    path("profile/requests/", views.ProfileUpdateRequestListView.as_view(), name="profile_request_list"),
    path("profile/requests/<int:pk>/handle/", views.HandleProfileUpdateRequestView.as_view(), name="handle_profile_request"),
    path("request-registration/", views.RegistrationRequestView.as_view(), name="request_registration"),
    path("api/locations/", views.UserLocationsAPI.as_view(), name="user_locations_api"),
]
