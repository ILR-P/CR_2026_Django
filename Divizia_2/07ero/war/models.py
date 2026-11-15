from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

MAX_HEALTH = 100


class Unit(models.Model):
    class UnitType(models.TextChoices):
        INFANTRY = "Infantry", "Infantry"
        CANNON = "Cannon", "Cannon"
        CAVALRY = "Cavalry", "Cavalry"
        KNIGHT = "Knight", "Knight"

    class Team(models.TextChoices):
        BLUE = "Blue", "Blue"
        RED = "Red", "Red"

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=UnitType.choices)
    team = models.CharField(max_length=10, choices=Team.choices)
    health = models.IntegerField(
        default=MAX_HEALTH,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_HEALTH)],
    )
    attack_points = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
    )
    profile_image_link = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.type}, {self.team})"

    @property
    def can_heal(self):
        return self.health < MAX_HEALTH

    def fights(self):
        return Fight.objects.filter(
            models.Q(fighter_a=self) | models.Q(fighter_b=self)
        ).order_by("-id")


class Fight(models.Model):
    fighter_a = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="fights_as_a")
    fighter_b = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="fights_as_b")
    winner = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="fights_won")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.fighter_a.name} vs {self.fighter_b.name}"


class FightStep(models.Model):
    fight = models.ForeignKey(Fight, on_delete=models.CASCADE, related_name="steps")
    order = models.PositiveIntegerField()
    attacker = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="+")
    defender = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="+")
    damage = models.IntegerField()
    attacker_health = models.IntegerField()
    defender_health = models.IntegerField()

    class Meta:
        ordering = ["order"]
