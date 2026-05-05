from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from .models import User, Profile

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, "profile"):
            context["profile_form"] = ProfileUpdateForm(instance=self.request.user.profile)
        else:
            context["profile_form"] = ProfileUpdateForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_form = UserUpdateForm(request.POST, request.FILES, instance=self.object)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=self.object.profile if hasattr(self.object, "profile") else None)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = self.object
            profile.save()
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=user_form, profile_form=profile_form))
