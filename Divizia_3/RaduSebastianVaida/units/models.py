
from django.db import models


class Unit(models.Model):

    UNIT_TYPES = [
        ("Infantry", "Infantry"),
        ("Cannon", "Cannon"),
        ("Cavalry", "Cavalry"),
        ("Knight", "Knight"),
    ]

    TEAMS = [
        ("Blue", "Blue"),
        ("Red", "Red"),
    ]

    name = models.CharField(max_length=100)

    type = models.CharField(
        max_length=20,
        choices=UNIT_TYPES
    )

    team = models.CharField(
        max_length=10,
        choices=TEAMS
    )

    health = models.IntegerField(
        default=100
    )

    attack_points = models.IntegerField()

    profile_image_link = models.URLField(
        max_length=500,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.name} ({self.type})"

    def heal(self):
        self.health = 100
        self.save()


class Fight(models.Model):

    unit1 = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="fights_as_unit1"
    )

    unit2 = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="fights_as_unit2"
    )

    winner = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="won_fights",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Fight #{self.id}: {self.unit1} vs {self.unit2}"


class FightTurn(models.Model):

    fight = models.ForeignKey(
        Fight,
        on_delete=models.CASCADE,
        related_name="turns"
    )

    attacker = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="attacks"
    )

    defender = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="defenses"
    )

    attack_points = models.IntegerField()

    attacker_health = models.IntegerField()

    defender_health = models.IntegerField()

    turn_number = models.IntegerField()

    def __str__(self):
        return f"Turn {self.turn_number} - Fight {self.fight.id}"
