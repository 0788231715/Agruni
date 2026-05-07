from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q, Max, Subquery, OuterRef
from accounts.models import User
from .models import Task, Message, StaffRoomMessage

class StaffRoomView(LoginRequiredMixin, View):
    template_name = "tasks/staff_room.html"

    def get(self, request):
        if request.user.role == User.Role.CUSTOMER:
            return redirect('dashboard:index')
        
        staff_messages = StaffRoomMessage.objects.all().order_by('created_at')
        return render(request, self.template_name, {
            'staff_messages': staff_messages
        })

    def post(self, request):
        if request.user.role == User.Role.CUSTOMER:
            return redirect('dashboard:index')

        content = request.POST.get('content')
        if content:
            StaffRoomMessage.objects.create(
                sender=request.user,
                content=content
            )
        return redirect('tasks:staff_room')

class ChatListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "tasks/chat_list.html"
    context_object_name = "staff_members"

    def get_queryset(self):
        # Only staff members can chat with each other
        user = self.request.user
        
        # Subquery to get the latest message content and timestamp for each user
        latest_message_subquery = Message.objects.filter(
            Q(sender=user, receiver=OuterRef('pk')) | Q(sender=OuterRef('pk'), receiver=user)
        ).order_by('-created_at')

        queryset = User.objects.exclude(role=User.Role.CUSTOMER).exclude(id=user.id).annotate(
            last_message_time=Max(
                Subquery(latest_message_subquery.values('created_at')[:1])
            ),
            last_message_content=Subquery(latest_message_subquery.values('content')[:1]),
            last_message_sender_id=Subquery(latest_message_subquery.values('sender_id')[:1]),
            last_message_is_read=Subquery(latest_message_subquery.values('is_read')[:1]),
        )
        
        # We need to manually calculate unread_count per user
        for u in queryset:
            u.unread_count = Message.objects.filter(sender=u, receiver=user, is_read=False).count()

        # Sort by last message time (descending), then by username
        return sorted(queryset, key=lambda x: (x.last_message_time or timezone.make_aware(timezone.datetime(1970, 1, 1))), reverse=True)

class ChatThreadView(LoginRequiredMixin, View):
    template_name = "tasks/chat_thread.html"

    def get(self, request, username):
        other_user = get_object_or_404(User, username=username)
        messages_list = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=request.user))
        ).order_by('created_at')

        # Mark received messages as read
        Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

        return render(request, self.template_name, {
            'other_user': other_user,
            'chat_messages': messages_list
        })

    def post(self, request, username):
        other_user = get_object_or_404(User, username=username)
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content
            )
        return redirect('tasks:chat_thread', username=username)

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "received_tasks"

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['created_tasks'] = Task.objects.filter(creator=self.request.user)
        return context

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.assignee == self.request.user and not obj.is_read:
            obj.is_read = True
            obj.read_at = timezone.now()
            obj.save()
        return obj

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ["assignee", "title", "description"]
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks:task_list")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.success(self.request, "Task assigned successfully.")
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Heads can only assign to subordinates (for simplicity, we'll allow all staff for now)
        form.fields['assignee'].queryset = User.objects.exclude(role=User.Role.CUSTOMER).exclude(id=self.request.user.id)
        return form

class TaskStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ["status"]
    success_url = reverse_lazy("tasks:task_list")

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        if task.assignee == request.user:
            task.status = request.POST.get("status")
            task.save()
            messages.success(request, f"Task status updated to {task.get_status_display()}.")
        return redirect(self.success_url)
