from django import forms
from payments.models import Payment

class ClientPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "payment_method", "transaction_id", "proof_image"]
        widgets = {
            'amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }
