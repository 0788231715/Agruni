from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from services.models import Service

class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = Service.objects.filter(is_active=True)[:3]
        return context

class AboutView(TemplateView):
    template_name = "core/about.html"

class ServicesView(ListView):
    model = Service
    template_name = "core/services.html"
    context_object_name = "services"
    queryset = Service.objects.filter(is_active=True)

class ContactView(TemplateView):
    template_name = "core/contact.html"

class ProjectsView(TemplateView):
    template_name = "core/projects.html"
