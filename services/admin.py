from django.contrib import admin
from .models import WasteCategory, Service

@admin.register(WasteCategory)
class WasteCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_recyclable", "created_at")
    search_fields = ("name",)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "service_type", "price", "is_active")
    list_filter = ("service_type", "is_active")
    search_fields = ("title",)
