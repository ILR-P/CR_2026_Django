from django import forms
from .models import Unit


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'unit_type', 'team', 'health', 'attack_points', 'profile_image_link']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter fighter name',
                'required': True,
            }),
            'unit_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'team': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'health': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'required': True,
            }),
            'attack_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50,
                'required': True,
            }),
            'profile_image_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://...',
                'required': True,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound and 'health' not in self.initial:
            self.initial['health'] = 100

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name is not None:
            name = name.strip()
            if not name:
                raise forms.ValidationError("Name cannot be empty.")
        return name
