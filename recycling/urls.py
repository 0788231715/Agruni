from django.urls import path
from . import views

app_name = "recycling"

urlpatterns = [
    path("records/", views.WasteSortingListView.as_view(), name="waste_records"),
    path("sorting/add/", views.WasteSortingCreateView.as_view(), name="sorting_add"),
    path("recycling/add/", views.RecyclingRecordCreateView.as_view(), name="recycling_add"),
    path("disposal/add/", views.DisposalRecordCreateView.as_view(), name="disposal_add"),
]
