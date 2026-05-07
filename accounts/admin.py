from django.contrib import admin
from .models import User, Profile, RegistrationRequest

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_verified")
    list_filter = ("role", "is_verified")
    search_fields = ("username", "email", "phone_number")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location")

@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone_number", "customer_type", "latitude", "longitude", "status", "created_at")
    list_filter = ("status", "customer_type")
    actions = ["approve_request"]

    def approve_request(self, request, queryset):
        # Logic to convert request to User could go here
        queryset.update(status="APPROVED")
    approve_request.short_description = "Mark selected requests as Approved"
