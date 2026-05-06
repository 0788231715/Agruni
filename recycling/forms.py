from django import forms
from .models import WasteSorting, RecyclingRecord, DisposalRecord

class WasteSortingForm(forms.ModelForm):
    class Meta:
        model = WasteSorting
        fields = ['pickup', 'category', 'weight_kg']

class RecyclingRecordForm(forms.ModelForm):
    class Meta:
        model = RecyclingRecord
        fields = ['sorting', 'processed_material', 'output_weight_kg', 'recycling_facility', 'completion_date', 'notes']
        widgets = {
            'completion_date': forms.DateInput(attrs={'type': 'date'}),
        }

class DisposalRecordForm(forms.ModelForm):
    class Meta:
        model = DisposalRecord
        fields = ['sorting', 'disposal_method', 'landfill_location', 'disposal_date', 'environmental_impact_notes']
        widgets = {
            'disposal_date': forms.DateInput(attrs={'type': 'date'}),
        }
