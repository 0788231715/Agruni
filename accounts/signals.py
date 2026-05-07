from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User, RegistrationRequest
from collection.models import ServiceRequest, DriverAssignment, Subscription
from core.models import Notification

@receiver(post_save, sender=Subscription)
def notify_new_subscription(sender, instance, created, **kwargs):
    if created:
        # Notify Admin
        admins = User.objects.filter(role=User.Role.ADMIN)
        from django.urls import reverse
        sub_url = reverse('collection:subscription_detail', kwargs={'pk': instance.pk})
        for admin in admins:
            Notification.objects.create(
                user=admin,
                title="New Service Agreement",
                message=f"A new agreement has been created for {instance.customer.username} in {instance.zone.name if instance.zone else 'No Zone'}.",
                link=sub_url
            )
        # Notify Customer
        Notification.objects.create(
            user=instance.customer,
            title="Service Agreement Active",
            message=f"Your waste management agreement is now active. Frequency: {instance.get_frequency_display()}.",
            link=sub_url
        )

@receiver(post_save, sender=User)
def notify_new_user(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance,
            title="Welcome to WMRS",
            message=f"Hello {instance.username}, your account has been created as a {instance.get_role_display()}."
        )
        # Notify Admin
        admins = User.objects.filter(role=User.Role.ADMIN)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                title="New User Registered",
                message=f"{instance.username} joined as {instance.get_role_display()}."
            )

@receiver(post_save, sender=RegistrationRequest)
def notify_reg_request(sender, instance, created, **kwargs):
    if created:
        targets = User.objects.filter(role__in=[User.Role.ADMIN, User.Role.SECRETARY])
        for target in targets:
            Notification.objects.create(
                user=target,
                title="New Registration Inquiry",
                message=f"New request from {instance.full_name}. Please review."
            )

@receiver(post_save, sender=ServiceRequest)
def notify_collector_assignment(sender, instance, created, **kwargs):
    # If a collector is assigned to a request
    if instance.collector:
        Notification.objects.create(
            user=instance.collector,
            title="New Collection Assigned",
            message=f"You have been assigned to collect from {instance.customer.username} on {instance.preferred_date}."
        )

@receiver(post_save, sender=DriverAssignment)
def notify_driver_assignment(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.driver,
            title="New Transport Task",
            message=f"New task: Transport waste for Request #{instance.request.id} using {instance.vehicle.plate_number}."
        )
