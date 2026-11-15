from django import forms
from .models import Unit

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'unit_type', 'team', 'health', 'attack_points', 'profile_image']
        widgets = {
            'health': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'attack_points': forms.NumberInput(attrs={'min': 0, 'max': 50}),
        }