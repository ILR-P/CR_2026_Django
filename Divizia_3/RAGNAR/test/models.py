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
    profile_image_link = models.URLField()

    def __str__(self):
        return f"{self.name} ({self.team} - {self.unit_type})"

class Fight(models.Model):
    fighter1 = models.ForeignKey(Unit, related_name='fights_as_fighter1', on_delete=models.CASCADE)
    fighter2 = models.ForeignKey(Unit, related_name='fights_as_fighter2', on_delete=models.CASCADE)
    winner = models.ForeignKey(Unit, related_name='fights_won', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        winner_name = self.winner.name if self.winner else "Draw/Ongoing"
        return f"Fight #{self.id}: {self.fighter1.name} vs {self.fighter2.name} (Winner: {winner_name})"

class FightHistory(models.Model):
    fight = models.ForeignKey(Fight, related_name='history_steps', on_delete=models.CASCADE)
    step_number = models.IntegerField()
    attacker = models.ForeignKey(Unit, related_name='attacks_made', on_delete=models.CASCADE)
    defender = models.ForeignKey(Unit, related_name='attacks_received', on_delete=models.CASCADE)
    damage_dealt = models.IntegerField()
    attacker_health_after = models.IntegerField()
    defender_health_after = models.IntegerField()

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"Step {self.step_number}: {self.attacker.name} hits {self.defender.name} for {self.damage_dealt} damage"