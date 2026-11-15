import random

from django.db import transaction
from django.db.models import Q, Sum

from .models import Fight, FightStep, Unit


def validate_pair(units):
    """Return an error message, or None if these units may fight."""
    if len(units) != 2:
        return "Select exactly two units."
    a, b = units
    if a.team == b.team:
        return "The two units must be from different teams."
    if a.health <= 0 or b.health <= 0:
        return "A unit with 0 health cannot fight. Heal it first."
    if a.attack_points == 0 and b.attack_points == 0:
        return "Neither unit can deal damage, the fight would never end."
    return None


@transaction.atomic
def simulate_fight(unit_a, unit_b):
    """unit_a attacks first, then they alternate until one has 0 health."""
    fight = Fight.objects.create(unit_a=unit_a, unit_b=unit_b)
    attacker, defender = unit_a, unit_b
    steps, order = [], 0

    while unit_a.health > 0 and unit_b.health > 0:
        order += 1
        points = random.randint(0, attacker.attack_points)
        damage = min(points, defender.health)
        defender.health -= damage
        steps.append(
            FightStep(
                fight=fight, order=order, attacker=attacker, defender=defender,
                points=points, damage=damage,
                attacker_health=attacker.health, defender_health=defender.health,
            )
        )
        attacker, defender = defender, attacker

    FightStep.objects.bulk_create(steps)
    unit_a.save(update_fields=["health"])
    unit_b.save(update_fields=["health"])
    fight.winner = unit_a if unit_a.health > 0 else unit_b
    fight.save(update_fields=["winner"])
    return fight


def team_stats():
    rows = []
    for team in Unit.Team.values:
        fights = Fight.objects.filter(Q(unit_a__team=team) | Q(unit_b__team=team)).distinct().count()
        caused = FightStep.objects.filter(attacker__team=team).aggregate(s=Sum("damage"))["s"] or 0
        taken = FightStep.objects.filter(defender__team=team).aggregate(s=Sum("damage"))["s"] or 0
        rows.append({"team": team, "fights": fights, "caused": caused, "taken": taken})
    return rows
