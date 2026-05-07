from django.db import models
from django.conf import settings
from services.models import Service, WasteCategory

class District(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Sector(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="sectors")
    name = models.CharField(max_length=100)
    def __str__(self): return f"{self.name} ({self.district.name})"

class Zone(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name="zones")
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'LOCATION_MANAGER'}, related_name="managed_zones")
    collectors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, limit_choices_to={'role': 'COLLECTOR'}, related_name="assigned_zones")
    def __str__(self): return f"{self.name} ({self.sector.name})"

class Vehicle(models.Model):
    class VehicleStatus(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        ON_ROUTE = "ON_ROUTE", "On Route"
        MAINTENANCE = "MAINTENANCE", "Maintenance"
        RETIRED = "RETIRED", "Retired"

    plate_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100)
    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=VehicleStatus.choices, default=VehicleStatus.AVAILABLE)
    last_service_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.model} ({self.plate_number})"

class Route(models.Model):
    name = models.CharField(max_length=100)
    area = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ServiceRequest(models.Model):
    class RequestStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        ASSIGNED = "ASSIGNED", "Assigned"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requests")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    waste_category = models.ForeignKey(WasteCategory, on_delete=models.SET_NULL, null=True)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True)
    location_details = models.TextField(help_text="Specific address or landmarks", default="")
    preferred_date = models.DateField()
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    collector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'COLLECTOR'}, related_name="assigned_requests")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request #{self.id} - {self.customer.username}"

class Subscription(models.Model):
    class Frequency(models.TextChoices):
        DAILY = "DAILY", "Daily"
        WEEKLY = "WEEKLY", "Weekly"
        BIWEEKLY = "BIWEEKLY", "Bi-Weekly"
        MONTHLY = "MONTHLY", "Monthly"
        CUSTOM = "CUSTOM", "Custom"

    class CustomerType(models.TextChoices):
        HOME = "HOME", "Home"
        BUILDING = "BUILDING", "Building"
        COMPANY = "COMPANY", "Company"
        INSTITUTION = "INSTITUTION", "Institution"
        SHOP = "SHOP", "Shop"
        RESTAURANT = "RESTAURANT", "Restaurant"
        HOTEL = "HOTEL", "Hotel"
        OTHER = "OTHER", "Other"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    customer_type = models.CharField(max_length=20, choices=CustomerType.choices, default=CustomerType.HOME)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True)
    collector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'COLLECTOR'})
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.WEEKLY)
    agreed_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sub #{self.id} - {self.customer.username}"

class DriverAssignment(models.Model):
    request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name="assignment")
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignments")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Assignment: {self.driver.username} to {self.request}"

class Pickup(models.Model):
    assignment = models.OneToOneField(DriverAssignment, on_delete=models.CASCADE, related_name="pickup")
    actual_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pickup_time = models.DateTimeField(auto_now_add=True)
    proof_image = models.ImageField(upload_to="pickups/", blank=True, null=True)
    customer_signature = models.ImageField(upload_to="signatures/", blank=True, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Pickup for {self.assignment.request}"
