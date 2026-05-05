from django.contrib import admin
from .models import Vehicle, Route, ServiceRequest, Subscription, DriverAssignment, Pickup

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("plate_number", "model", "capacity_kg", "status")
    list_filter = ("status",)

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "service", "status", "preferred_date")
    list_filter = ("status", "service")
    search_fields = ("customer__username", "location")

@admin.register(DriverAssignment)
class DriverAssignmentAdmin(admin.ModelAdmin):
    list_display = ("request", "driver", "vehicle", "assigned_at", "completed_at")
    list_filter = ("driver", "vehicle")

admin.site.register(Route)
admin.site.register(Subscription)
admin.site.register(Pickup)
