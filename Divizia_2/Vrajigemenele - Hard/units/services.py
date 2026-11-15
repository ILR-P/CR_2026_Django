import random

from django.db import transaction
from django.db.models import Count, Q, Sum

from .models import MAX_HEALTH, Fight, FightStep, Unit

MAX_STEPS = 100_000  # safety net, a fight can't realistically get near this


def heal(unit_id):
    Unit.objects.filter(pk=unit_id).update(health=MAX_HEALTH)


def run_fight(unit_a_id, unit_b_id, rng=random):
    """Fighters take turns (a first); each hit is rng(0..attack_points). Health is
    saved on the units and every hit is saved as a FightStep. Rows are locked
    so two simultaneous fights can't corrupt a shared unit's health."""
    with transaction.atomic():
        locked = {u.pk: u for u in Unit.objects.select_for_update().filter(pk__in=[unit_a_id, unit_b_id]).order_by("pk")}
        a, b = locked[unit_a_id], locked[unit_b_id]
        fight = Fight.objects.create(unit_a=a, unit_b=b)
        steps, attacker, defender = [], a, b
        while a.health > 0 and b.health > 0 and len(steps) < MAX_STEPS:
            points = rng.randint(0, attacker.attack_points)
            defender.health = max(0, defender.health - points)
            steps.append(FightStep(
                fight=fight, number=len(steps) + 1, attacker=attacker, defender=defender,
                points=points, attacker_health=attacker.health, defender_health=defender.health,
            ))
            attacker, defender = defender, attacker
        winner = a if a.health > 0 else b
        fight.winner = winner
        fight.save(update_fields=["winner"])
        FightStep.objects.bulk_create(steps)
        Unit.objects.bulk_update([a, b], ["health"])
    return fight


def team_stats():
    """Per team: fights fought, fights won, damage caused, damage taken. Computed
    from the saved fight histories."""
    out = []
    for team, label in Unit.Team.choices:
        fights = Fight.objects.filter(Q(unit_a__team=team) | Q(unit_b__team=team)).count()
        won = Fight.objects.filter(winner__team=team).count()
        caused = FightStep.objects.filter(attacker__team=team).aggregate(t=Sum("points"))["t"] or 0
        taken = FightStep.objects.filter(defender__team=team).aggregate(t=Sum("points"))["t"] or 0
        out.append({"team": team, "label": label, "fights": fights, "won": won, "caused": caused, "taken": taken})
    return out
