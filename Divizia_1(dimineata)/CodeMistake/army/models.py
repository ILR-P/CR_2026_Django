from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Unit(models.Model):

    TYPES = [
        ('Infantry', 'Infantry'),
        ('Cannon', 'Cannon'),
        ('Cavalry', 'Cavalry'),
        ('Knight', 'Knight'),
    ]

    TEAMS = [
        ('Blue', 'Blue'),
        ('Red', 'Red'),
    ]

    name = models.CharField(max_length=100)

    type = models.CharField(
        max_length=20,
        choices=TYPES
    )

    team = models.CharField(
        max_length=10,
        choices=TEAMS
    )

    health = models.IntegerField(
        default=100,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    attack_points = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(50)
        ]
    )

    profile_image_link = models.URLField()

    def __str__(self):
        return self.name