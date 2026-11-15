from django import forms

from .models import MAX_ATTACK, MAX_HEALTH, Unit


class UnitForm(forms.ModelForm):
    health = forms.IntegerField(min_value=0, max_value=MAX_HEALTH, initial=MAX_HEALTH)
    attack_points = forms.IntegerField(
        label="Attack points", min_value=0, max_value=MAX_ATTACK
    )

    class Meta:
        model = Unit
        fields = ["name", "unit_type", "team", "health", "attack_points", "profile_image_link"]
