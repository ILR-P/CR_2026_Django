from celery import shared_task
from django.db import transaction
from django.db.models import F, Value
from django.db.models.functions import Greatest

from .models import Fight, FightEvent, Person


@shared_task
def simulate_fight(fight_id):
    # Revendică lupta atomic: dacă task-ul rulează de două ori, doar unul câștigă.
    if not Fight.objects.filter(pk=fight_id, status=Fight.QUEUED).update(status=Fight.RUNNING):
        return "skipped"
    try:
        taken = {}
        for ev in FightEvent.objects.filter(fight_id=fight_id).order_by("sequence"):
            with transaction.atomic():
                # Scădere atomică în DB (nu citește-modifică-scrie în Python), deci
                # lupte paralele cu același soldat nu își suprascriu modificările.
                Person.objects.filter(pk=ev.defender_id).update(
                    health=Greatest(F("health") - ev.damage, Value(0))
                )
                health = Person.objects.values_list("health", flat=True).get(pk=ev.defender_id)
                FightEvent.objects.filter(pk=ev.pk).update(defender_health_after=health)
            taken[ev.defender_id] = taken.get(ev.defender_id, 0) + ev.damage

        fight = Fight.objects.get(pk=fight_id)
        a, b = taken.get(fight.soldier_a_id, 0), taken.get(fight.soldier_b_id, 0)
        winner_id = fight.soldier_b_id if a > b else fight.soldier_a_id if b > a else None
        Fight.objects.filter(pk=fight_id).update(status=Fight.DONE, winner_id=winner_id)
    except Exception:
        Fight.objects.filter(pk=fight_id).update(status=Fight.FAILED)
        raise