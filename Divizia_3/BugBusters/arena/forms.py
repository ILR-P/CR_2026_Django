from django import forms
from .models import Fighter


class FighterForm(forms.ModelForm):
    class Meta:
        model = Fighter
        fields = ('name', 'type', 'health', 'attack_points')
