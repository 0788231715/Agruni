from django import forms
from .models import Payment, MoneyHandover, Expense

class ClientPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "payment_method", "transaction_id", "proof_image"]
        widgets = {
            'amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }

class ReportPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "payment_method", "transaction_id", "proof_image"]
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount paid'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction ID / Reference'}),
            'proof_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["invoice", "amount", "payment_method", "transaction_id", "proof_image"]

class MoneyHandoverForm(forms.ModelForm):
    class Meta:
        model = MoneyHandover
        fields = ["to_user", "amount", "payments", "zone", "notes"]

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["category", "amount", "description", "date", "proof_image"]
