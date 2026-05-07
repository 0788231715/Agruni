from django import forms
from .models import ServiceRequest, Subscription, Zone

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ["service", "waste_category", "zone", "location_details", "preferred_date", "notes"]
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'location_details': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class SubscriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import User
        self.fields['customer'].queryset = User.objects.filter(role=User.Role.CUSTOMER)

    class Meta:
        model = Subscription
        fields = ["customer", "customer_type", "service", "zone", "frequency", "agreed_fee", "start_date", "end_date"]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
