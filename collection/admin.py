from django.contrib import admin
from .models import Vehicle, Route, ServiceRequest, Subscription, DriverAssignment, Pickup, District, Sector, Zone

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ("name", "district")

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "sector", "manager")

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("plate_number", "model", "capacity_kg", "status")
    list_filter = ("status",)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("name", "area")

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "service", "zone", "status", "created_at")
    list_filter = ("status", "service", "zone")
    search_fields = ("customer__username", "location_details")

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "service", "frequency", "agreed_fee", "is_active")
    list_filter = ("frequency", "is_active")

@admin.register(DriverAssignment)
class DriverAssignmentAdmin(admin.ModelAdmin):
    list_display = ("request", "driver", "vehicle", "assigned_at")

@admin.register(Pickup)
class PickupAdmin(admin.ModelAdmin):
    list_display = ("assignment", "actual_weight_kg", "pickup_time")
