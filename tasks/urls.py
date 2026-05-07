from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.TaskListView.as_view(), name="task_list"),
    path("create/", views.TaskCreateView.as_view(), name="task_create"),
    path("<int:pk>/", views.TaskDetailView.as_view(), name="task_detail"),
    path("<int:pk>/status/", views.TaskStatusUpdateView.as_view(), name="task_status_update"),
    path("chat/", views.ChatListView.as_view(), name="chat_list"),
    path("chat/staff-room/", views.StaffRoomView.as_view(), name="staff_room"),
    path("chat/<str:username>/", views.ChatThreadView.as_view(), name="chat_thread"),
]
