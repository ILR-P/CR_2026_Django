import random

from django.db import transaction
from django.db.models import Q, Sum

from .models import Fight, FightStep, Unit


class FightError(Exception):
    pass


@transaction.atomic
def simulate_fight(unit_a, unit_b, rng=random):
    """Fighters alternate attacks (unit_a first) until one has no health left.
    Each attack deals a random 0..attack_points damage. Health changes are saved
    on the units and every attack is stored as a FightStep."""
    if unit_a.pk == unit_b.pk:
        raise FightError("Choose two different fighters.")
    if unit_a.team == unit_b.team:
        raise FightError("Fighters must belong to different teams.")
    if unit_a.health <= 0 or unit_b.health <= 0:
        raise FightError("Both fighters need some health left. Heal them first.")
    if unit_a.attack_points == 0 and unit_b.attack_points == 0:
        raise FightError("Neither fighter can deal damage, the fight would never end.")

    fight = Fight.objects.create(fighter_a=unit_a, fighter_b=unit_b, winner=unit_a)
    attacker, defender = unit_a, unit_b
    order = 1
    while unit_a.health > 0 and unit_b.health > 0:
        damage = rng.randint(0, attacker.attack_points)
        defender.health = max(0, defender.health - damage)
        FightStep.objects.create(
            fight=fight, order=order, attacker=attacker, defender=defender,
            damage=damage, attacker_health=attacker.health, defender_health=defender.health,
        )
        order += 1
        attacker, defender = defender, attacker
    fight.winner = unit_a if unit_a.health > 0 else unit_b
    fight.save(update_fields=["winner"])
    unit_a.save(update_fields=["health"])
    unit_b.save(update_fields=["health"])
    return fight


def team_statistics():
    stats = []
    for team in Unit.Team.values:
        fights = Fight.objects.filter(
            Q(fighter_a__team=team) | Q(fighter_b__team=team)
        ).count()
        caused = FightStep.objects.filter(attacker__team=team).aggregate(s=Sum("damage"))["s"] or 0
        taken = FightStep.objects.filter(defender__team=team).aggregate(s=Sum("damage"))["s"] or 0
        stats.append({"team": team, "fights": fights, "damage_caused": caused, "damage_taken": taken})
    return stats
