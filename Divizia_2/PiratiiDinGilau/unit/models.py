from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class FighterUnit(models.Model):
    UNIT_TYPES = (
        ('Infantry', 'Infantry'),
        ('Cannon', 'Cannon'),
        ('Cavalry', 'Cavalry'),
        ('Knight', 'Knight'),
    )

    TEAM_CHOICES = (
        ('Blue', 'Blue Team'),
        ('Red', 'Red Team'),
    )

    name = models.CharField(max_length=100)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES)
    team = models.CharField(max_length=10, choices=TEAM_CHOICES)

    health = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    attack_points = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )

    profile_image = models.URLField(max_length=500)

    def __str__(self):
        return f"{self.name} ({self.team} {self.unit_type})"


class FightHistory(models.Model):
    attacker = models.ForeignKey(FighterUnit, on_delete=models.CASCADE, related_name='fights_as_attacker')
    defender = models.ForeignKey(FighterUnit, on_delete=models.CASCADE, related_name='fights_as_defender')

    winner = models.ForeignKey(FighterUnit, on_delete=models.CASCADE, related_name='fights_won', null=True, blank=True)

    fight_log = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fight: {self.attacker.name} vs {self.defender.name}"