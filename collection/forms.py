from django import forms
from .models import ServiceRequest

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ["service", "waste_category", "location", "preferred_date", "notes"]
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'location': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
