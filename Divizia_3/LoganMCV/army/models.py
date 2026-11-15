from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

MAX_HEALTH = 100
MAX_ATTACK = 50


class Unit(models.Model):
    class UnitType(models.TextChoices):
        INFANTRY = "Infantry"
        CANNON = "Cannon"
        CAVALRY = "Cavalry"
        KNIGHT = "Knight"

    class Team(models.TextChoices):
        BLUE = "Blue"
        RED = "Red"

    name = models.CharField(max_length=100)
    unit_type = models.CharField("Type", max_length=20, choices=UnitType.choices)
    team = models.CharField(max_length=10, choices=Team.choices)
    health = models.IntegerField(
        default=MAX_HEALTH,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_HEALTH)],
    )
    attack_points = models.IntegerField(
        "Attack points",
        validators=[MinValueValidator(0), MaxValueValidator(MAX_ATTACK)],
    )
    profile_image_link = models.URLField("Profile image link", blank=True)

    class Meta:
        ordering = ["id"]

    @property
    def needs_heal(self):
        return self.health < MAX_HEALTH

    def __str__(self):
        return f"{self.name} ({self.unit_type}, {self.team})"


class Fight(models.Model):
    unit_a = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="fights_as_a")
    unit_b = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="fights_as_b")
    winner = models.ForeignKey(
        Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name="fights_won"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.unit_a.name} vs {self.unit_b.name}"


class FightStep(models.Model):
    """One attack in a fight."""

    fight = models.ForeignKey(Fight, on_delete=models.CASCADE, related_name="steps")
    order = models.PositiveIntegerField()
    attacker = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="+")
    defender = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="+")
    points = models.IntegerField()          # the random roll
    damage = models.IntegerField()          # damage really applied (roll capped at remaining HP)
    attacker_health = models.IntegerField()  # health status after this attack
    defender_health = models.IntegerField()

    class Meta:
        ordering = ["fight_id", "order"]
