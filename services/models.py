from django.db import models

class WasteCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_recyclable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Waste Categories"

class Service(models.Model):
    class ServiceType(models.TextChoices):
        COLLECTION = "COLLECTION", "Waste Collection"
        RECYCLING = "RECYCLING", "Recycling"
        CLEANING = "CLEANING", "Environmental Cleaning"
        PROJECT = "PROJECT", "Special Project"

    title = models.CharField(max_length=200)
    description = models.TextField()
    service_type = models.CharField(max_length=20, choices=ServiceType.choices, default=ServiceType.COLLECTION)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base price for the service")
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
