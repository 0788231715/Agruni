from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Admin / Boss / Owner")
        SECRETARY = "SECRETARY", _("Secretary / Registrar")
        GENERAL_MANAGER = "GENERAL_MANAGER", _("General Manager")
        LOCATION_MANAGER = "LOCATION_MANAGER", _("Location Manager")
        FINANCE = "FINANCE", _("Finance Officer")
        SUPERVISOR = "SUPERVISOR", _("Supervisor")
        COLLECTOR = "COLLECTOR", _("Collector / Employee")
        DRIVER = "DRIVER", _("Driver")
        CUSTOMER = "CUSTOMER", _("Customer / Client")
        SORTING_STAFF = "SORTING_STAFF", _("Sorting / Recycling Staff")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_online(self):
        if self.last_seen:
            from django.utils import timezone
            now = timezone.now()
            return now - self.last_seen < timezone.timedelta(minutes=5)
        return False

    @property
    def unread_notifications(self):
        return self.notifications.filter(is_read=False)

    @property
    def unread_notifications_count(self):
        return self.unread_notifications.count()

    @property
    def unread_tasks(self):
        return self.assigned_tasks.filter(is_read=False)

    @property
    def unread_tasks_count(self):
        return self.unread_tasks.count()

    @property
    def unread_messages_count(self):
        return self.received_messages.filter(is_read=False).count()

    def save(self, *args, **kwargs):
        # Automatically set staff/superuser status based on role
        if self.role in [self.Role.ADMIN, self.Role.SECRETARY, self.Role.GENERAL_MANAGER]:
            self.is_staff = True
            self.is_superuser = True
        elif self.role in [
            self.Role.LOCATION_MANAGER,
            self.Role.FINANCE,
            self.Role.SUPERVISOR
        ]:
            self.is_staff = True
            self.is_superuser = False
        else:
            self.is_staff = False
            self.is_superuser = False
        
        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

class RegistrationRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    customer_type = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request from {self.full_name}"
