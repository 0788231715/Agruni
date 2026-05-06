from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import WasteSorting, RecyclingRecord, DisposalRecord
from .forms import WasteSortingForm, RecyclingRecordForm, DisposalRecordForm

class WasteSortingListView(LoginRequiredMixin, ListView):
    model = WasteSorting
    template_name = "recycling/waste_records.html"
    context_object_name = "sortings"
    paginate_by = 20

    def get_queryset(self):
        return WasteSorting.objects.all().order_by('-sorting_date')

class WasteSortingCreateView(LoginRequiredMixin, CreateView):
    model = WasteSorting
    form_class = WasteSortingForm
    template_name = "recycling/sorting_form.html"
    success_url = reverse_lazy("recycling:waste_records")

    def form_valid(self, form):
        form.instance.sorted_by = self.request.user
        return super().form_valid(form)

class RecyclingRecordCreateView(LoginRequiredMixin, CreateView):
    model = RecyclingRecord
    form_class = RecyclingRecordForm
    template_name = "recycling/processing_form.html"
    success_url = reverse_lazy("dashboard:index")

    def get_initial(self):
        initial = super().get_initial()
        sorting_id = self.request.GET.get('sorting')
        if sorting_id:
            initial['sorting'] = sorting_id
        return initial

class DisposalRecordCreateView(LoginRequiredMixin, CreateView):
    model = DisposalRecord
    form_class = DisposalRecordForm
    template_name = "recycling/processing_form.html"
    success_url = reverse_lazy("dashboard:index")

    def get_initial(self):
        initial = super().get_initial()
        sorting_id = self.request.GET.get('sorting')
        if sorting_id:
            initial['sorting'] = sorting_id
        return initial
