from django import forms
from .models import Unit

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'unit_type', 'team', 'health', 'attack_points', 'profile_image_link']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit Name'}),
            'unit_type': forms.Select(attrs={'class': 'form-select'}),
            'team': forms.Select(attrs={'class': 'form-select'}),
            'health': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'attack_points': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 50}),
            'profile_image_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }
