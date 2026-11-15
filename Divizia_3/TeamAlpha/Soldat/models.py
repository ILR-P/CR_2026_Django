from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Unit(models.Model):
    TYPE_CHOICES = [
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
    unit_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    team = models.CharField(max_length=10, choices=TEAM_CHOICES)
    health = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    attack_points = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    profile_image_link = models.URLField(max_length=500)

    def __str__(self):
        return f"{self.name} ({self.team} - {self.unit_type})"


class Fight(models.Model):
    fighter1 = models.ForeignKey(Unit, related_name='fights_as_f1', on_delete=models.CASCADE)
    fighter2 = models.ForeignKey(Unit, related_name='fights_as_f2', on_delete=models.CASCADE)
    winner = models.ForeignKey(Unit, related_name='fights_won', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fighter1.name} vs {self.fighter2.name}"


class FightStep(models.Model):
    fight = models.ForeignKey(Fight, related_name='steps', on_delete=models.CASCADE)
    attacker = models.ForeignKey(Unit, related_name='attacks_made', on_delete=models.CASCADE)
    defender = models.ForeignKey(Unit, related_name='attacks_received', on_delete=models.CASCADE)
    damage = models.IntegerField()
    attacker_health_after = models.IntegerField()
    defender_health_after = models.IntegerField()
