from django.contrib import admin
from .models import Task, Message, StaffRoomMessage

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "assignee", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "description", "assignee__username")

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "content", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("content", "sender__username", "receiver__username")

@admin.register(StaffRoomMessage)
class StaffRoomMessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "content", "created_at")
    list_filter = ("created_at",)
    search_fields = ("content", "sender__username")
