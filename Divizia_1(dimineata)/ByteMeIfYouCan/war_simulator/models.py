from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Unit(models.Model):
    UNIT_TYPE_CHOICES = [
        ('Infantry', 'Infantry'),
        ('Cannon', 'Cannon'),
        ('Cavalry', 'Cavalry'),
        ('Knight', 'Knight'),
    ]

    TEAM_CHOICES = [
        ('Blue', 'Blue'),
        ('Red', 'Red'),
    ]

    name = models.CharField(max_length=100)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPE_CHOICES)
    team = models.CharField(max_length=10, choices=TEAM_CHOICES)
    health = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    attack_points = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    profile_image_link = models.URLField(max_length=500)

    def clean(self):
        super().clean()
        if self.name is not None and self.name != '' and not self.name.strip():
            raise ValidationError({'name': 'Name cannot be empty.'})

    def __str__(self):
        return f"{self.name} ({self.team} {self.unit_type})"


class Fight(models.Model):
    fighter_1 = models.ForeignKey(
        Unit,
        related_name='fights_as_first',
        on_delete=models.CASCADE
    )
    fighter_2 = models.ForeignKey(
        Unit,
        related_name='fights_as_second',
        on_delete=models.CASCADE
    )
    winner = models.ForeignKey(
        Unit,
        related_name='fights_won',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        winner_name = self.winner.name if self.winner else 'Draw/Ongoing'
        return f"Fight #{self.id}: {self.fighter_1.name} vs {self.fighter_2.name} (Winner: {winner_name})"


class FightStep(models.Model):
    fight = models.ForeignKey(
        Fight,
        related_name='steps',
        on_delete=models.CASCADE
    )
    step_number = models.PositiveIntegerField()
    attacker = models.ForeignKey(
        Unit,
        related_name='attacks_made',
        on_delete=models.CASCADE
    )
    defender = models.ForeignKey(
        Unit,
        related_name='attacks_received',
        on_delete=models.CASCADE
    )
    damage = models.PositiveIntegerField()
    attacker_health_after = models.IntegerField()
    defender_health_after = models.IntegerField()

    def __str__(self):
        return (
            f"Step {self.step_number} in Fight {self.fight_id}: "
            f"{self.attacker.name} attacked {self.defender.name} for {self.damage} dmg"
        )
