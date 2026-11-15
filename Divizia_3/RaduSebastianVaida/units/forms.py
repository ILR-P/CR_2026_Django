
from django import forms
from .models import Unit


class UnitForm(forms.ModelForm):

    class Meta:
        model = Unit

        fields = [
            "name",
            "type",
            "team",
            "health",
            "attack_points",
            "profile_image_link"
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Enter fighter name"
            }),

            "type": forms.Select(),

            "team": forms.Select(),

            "health": forms.NumberInput(attrs={
                "min": 0,
                "max": 100
            }),

            "attack_points": forms.NumberInput(attrs={
                "min": 0,
                "max": 50
            }),

            "profile_image_link": forms.URLInput(attrs={
                "placeholder": "Enter image URL"
            }),
        }

    def clean_health(self):
        health = self.cleaned_data["health"]

        if not 0 <= health <= 100:
            raise forms.ValidationError(
                "Health must be between 0 and 100."
            )

        return health

    def clean_attack_points(self):
        attack = self.cleaned_data["attack_points"]

        if not 0 <= attack <= 50:
            raise forms.ValidationError(
                "Attack points must be between 0 and 50."
            )

        return attack
