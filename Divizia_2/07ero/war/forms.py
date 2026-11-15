from django import forms

from .models import MAX_HEALTH, Unit


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["name", "type", "team", "health", "attack_points", "profile_image_link"]
        labels = {"attack_points": "Attack points", "profile_image_link": "Profile image link"}
        widgets = {
            "name": forms.TextInput(),
            "type": forms.Select(),
            "team": forms.Select(),
            "health": forms.NumberInput(attrs={"min": 0, "max": MAX_HEALTH}),
            "attack_points": forms.NumberInput(attrs={"min": 0, "max": 50}),
            "profile_image_link": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Name cannot be empty.")
        return name
