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

    DEFAULT_IMAGES = {
        'Infantry': 'https://i.pinimg.com/originals/4e/62/23/4e6223143c15f9def05dc8ca45f22a1d.gif',
        'Cannon': 'https://i.pinimg.com/736x/b2/44/e1/b244e1fafe20ffce49441d0cc7675a05.jpg',
        'Cavalry': 'https://i.pinimg.com/236x/08/f8/4e/08f84e797d04f505f6323b775bed4c7c.jpg',
        'Knight': 'https://i.pinimg.com/736x/75/84/74/758474da2fd87787c265b4ce2849fb14.jpg',
    }

    name = models.CharField(max_length=100)
    unit_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    team = models.CharField(max_length=10, choices=TEAM_CHOICES)
    health = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])
    attack_points = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    profile_image = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if not self.profile_image:
            self.profile_image = self.DEFAULT_IMAGES.get(
                self.unit_type,
                'https://placehold.co/50'
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.team})"


class Fight(models.Model):
    fighter1 = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='fights_as_f1')
    fighter2 = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='fights_as_f2')
    winner = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, related_name='fights_won')
    created_at = models.DateTimeField(auto_now_add=True)


class FightStep(models.Model):
    fight = models.ForeignKey(Fight, on_delete=models.CASCADE, related_name='steps')
    attacker = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='attacks_made')
    defender = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='attacks_received')
    damage = models.IntegerField()
    attacker_health_after = models.IntegerField()
    defender_health_after = models.IntegerField()