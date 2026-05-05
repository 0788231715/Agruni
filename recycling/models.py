from django.db import models
from collection.models import Pickup
from services.models import WasteCategory

class WasteSorting(models.Model):
    pickup = models.ForeignKey(Pickup, on_delete=models.CASCADE, related_name="sortings")
    category = models.ForeignKey(WasteCategory, on_delete=models.CASCADE)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    sorting_date = models.DateTimeField(auto_now_add=True)
    sorted_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.category.name} - {self.weight_kg}kg"

class RecyclingRecord(models.Model):
    sorting = models.OneToOneField(WasteSorting, on_delete=models.CASCADE, related_name="recycling")
    processed_material = models.CharField(max_length=100)
    output_weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    recycling_facility = models.CharField(max_length=200)
    completion_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Recycled: {self.processed_material}"

class DisposalRecord(models.Model):
    sorting = models.OneToOneField(WasteSorting, on_delete=models.CASCADE, related_name="disposal")
    disposal_method = models.CharField(max_length=100)
    landfill_location = models.CharField(max_length=200)
    disposal_date = models.DateField()
    environmental_impact_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Disposed via {self.disposal_method}"
