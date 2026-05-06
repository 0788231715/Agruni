from django.contrib import admin
from .models import Expense, Invoice, Payment, MoneyHandover, SalaryOrCommission

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("category", "amount", "date", "recorded_by")
    list_filter = ("category", "date")

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "amount", "due_date", "status")
    list_filter = ("status", "due_date")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "invoice", "amount", "payment_method", "collected_by", "is_verified")
    list_filter = ("payment_method", "is_verified")

@admin.register(MoneyHandover)
class MoneyHandoverAdmin(admin.ModelAdmin):
    list_display = ("id", "from_user", "to_user", "amount", "status", "created_at")
    list_filter = ("status",)

@admin.register(SalaryOrCommission)
class SalaryOrCommissionAdmin(admin.ModelAdmin):
    list_display = ("employee", "amount", "period_start", "period_end", "is_paid")
    list_filter = ("is_paid",)
