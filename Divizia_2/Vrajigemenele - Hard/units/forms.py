from django import forms

from .models import Unit


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["name", "type", "team", "health", "attack_points", "profile_image_link"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Sir Lancelot", "autofocus": True}),
            "health": forms.NumberInput(attrs={"min": 0, "max": 100}),
            "attack_points": forms.NumberInput(attrs={"min": 0, "max": 50}),
            "profile_image_link": forms.URLInput(attrs={"placeholder": "https://…/portrait.png"}),
        }
        help_texts = {
            "health": "0 – 100 (default 100)",
            "attack_points": "0 – 50",
            "profile_image_link": "Optional. A picture of the fighter.",
        }


class FightForm(forms.Form):
    """Two ticked units of different teams, both alive, able to hurt each other."""

    units = forms.ModelMultipleChoiceField(queryset=Unit.objects.all(), error_messages={"required": "Select two units to fight."})

    def clean_units(self):
        units = list(self.cleaned_data["units"])
        if len(units) != 2:
            raise forms.ValidationError("Select exactly two units.")
        a, b = units
        if a.team == b.team:
            raise forms.ValidationError("The fighters must be on different teams.")
        if a.health == 0 or b.health == 0:
            raise forms.ValidationError("A unit with 0 health can't fight — heal it first.")
        if a.attack_points == 0 and b.attack_points == 0:
            raise forms.ValidationError("Neither unit can deal damage, the fight would never end.")
        return units
