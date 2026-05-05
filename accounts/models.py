from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        PUBLIC = "PUBLIC", _("Public Visitor")
        CUSTOMER = "CUSTOMER", _("Customer")
        DRIVER = "DRIVER", _("Driver / Collection Staff")
        SORTING_STAFF = "SORTING_STAFF", _("Sorting and Recycling Staff")
        SUPERVISOR = "SUPERVISOR", _("Operations Supervisor")
        FINANCE = "FINANCE", _("Finance Officer")
        MANAGER = "MANAGER", _("Company Manager")
        ADMIN = "ADMIN", _("System Administrator")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
