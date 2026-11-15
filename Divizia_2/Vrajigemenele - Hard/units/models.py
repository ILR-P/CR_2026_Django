from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse

MAX_HEALTH = 100
MAX_ATTACK = 50


class Unit(models.Model):
    class Type(models.TextChoices):
        INFANTRY = "infantry", "Infantry"
        CANNON = "cannon", "Cannon"
        CAVALRY = "cavalry", "Cavalry"
        KNIGHT = "knight", "Knight"

    class Team(models.TextChoices):
        BLUE = "blue", "Blue"
        RED = "red", "Red"

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=Type)
    team = models.CharField(max_length=4, choices=Team)
    health = models.PositiveSmallIntegerField(
        default=MAX_HEALTH, validators=[MinValueValidator(0), MaxValueValidator(MAX_HEALTH)]
    )
    attack_points = models.PositiveSmallIntegerField(
        default=10, validators=[MinValueValidator(0), MaxValueValidator(MAX_ATTACK)]
    )
    profile_image_link = models.URLField(blank=True, max_length=500, verbose_name="profile image link")

    class Meta:
        ordering = ["name", "id"]
        constraints = [
            models.CheckConstraint(condition=Q(health__gte=0, health__lte=MAX_HEALTH), name="unit_health_range"),
            models.CheckConstraint(condition=Q(attack_points__gte=0, attack_points__lte=MAX_ATTACK), name="unit_attack_range"),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()}, {self.get_team_display()})"

    def get_absolute_url(self):
        return reverse("unit-detail", args=[self.pk])

    @property
    def needs_heal(self):
        return self.health < MAX_HEALTH

    @property
    def initials(self):
        return "".join(w[0] for w in self.name.split()[:2]).upper() or "?"


class Fight(models.Model):
    unit_a = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="fights_as_a")
    unit_b = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="fights_as_b")
    winner = models.ForeignKey(Unit, null=True, on_delete=models.SET_NULL, related_name="fights_won")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"Fight #{self.pk}: {self.unit_a.name} vs {self.unit_b.name}"


class FightStep(models.Model):
    """One attack of a fight, saved step by step."""

    fight = models.ForeignKey(Fight, on_delete=models.CASCADE, related_name="steps")
    number = models.PositiveIntegerField()
    attacker = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="attacks")
    defender = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="hits_taken")
    points = models.PositiveSmallIntegerField()
    attacker_health = models.PositiveSmallIntegerField()
    defender_health = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["fight", "number"]
        constraints = [models.UniqueConstraint(fields=["fight", "number"], name="uniq_step_per_fight")]

    def __str__(self):
        return f"{self.attacker.name} hits {self.defender.name} for {self.points}"
