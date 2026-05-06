from django.db import models
from django.conf import settings
from collection.models import ServiceRequest, Subscription, Zone

class Expense(models.Model):
    class ExpenseCategory(models.TextChoices):
        FUEL = "FUEL", "Fuel"
        MAINTENANCE = "MAINTENANCE", "Vehicle Maintenance"
        SALARY = "SALARY", "Staff Salary"
        COMMISSION = "COMMISSION", "Collector Commission"
        OFFICE = "OFFICE", "Office Supplies"
        OTHER = "OTHER", "Other"

    category = models.CharField(max_length=20, choices=ExpenseCategory.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateField()
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    proof_image = models.ImageField(upload_to="expenses/", blank=True, null=True)

    def __str__(self):
        return f"{self.category} - {self.amount} on {self.date}"

class Invoice(models.Model):
    class InvoiceStatus(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"
        PARTIAL = "PARTIAL", "Partially Paid"
        OVERDUE = "OVERDUE", "Overdue"

    request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name="invoice", null=True, blank=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="invoices", null=True, blank=True)
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.UNPAID)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number}"

class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
        ONLINE = "ONLINE", "Online Payment"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    collected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="collected_payments")
    payment_date = models.DateTimeField(auto_now_add=True)
    proof_image = models.ImageField(upload_to="payments/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment {self.id} for {self.invoice.invoice_number}"

class MoneyHandover(models.Model):
    class HandoverStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RECEIVED = "RECEIVED", "Received/Verified"
        REJECTED = "REJECTED", "Rejected"

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="handovers_sent")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="handovers_received")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payments = models.ManyToManyField(Payment, related_name="handovers")
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=HandoverStatus.choices, default=HandoverStatus.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Handover {self.id}: {self.from_user.username} -> {self.to_user.username}"

class SalaryOrCommission(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="earnings")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.employee.username} - {self.amount} ({self.period_start} to {self.period_end})"
