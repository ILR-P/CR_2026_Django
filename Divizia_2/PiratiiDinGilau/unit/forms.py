from django import forms
from .models import FighterUnit

class FighterUnitForm(forms.ModelForm):
    class Meta:
        model = FighterUnit
        fields = ['name', 'unit_type', 'team', 'health', 'attack_points', 'profile_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_type': forms.Select(attrs={'class': 'form-control'}),
            'team': forms.Select(attrs={'class': 'form-control'}),
            'health': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'attack_points': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 50}),
            'profile_image': forms.URLInput(attrs={'class': 'form-control'}),
        }