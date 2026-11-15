"""Importing people / fights and the per-fight simulation logic."""

from django.db import transaction
from django.db.models import F, Value
from django.db.models.functions import Greatest
from django.utils import timezone

from .models import MAX_HEALTH, Fight, FightEvent, Person, Soldier


# Rank label -> model value map (case-insensitive).
# The /draft endpoint sends the human-readable label (e.g. "Lieutenant").
_RANK_LABEL_MAP = {r.label.lower(): r.value for r in Person.Rank}


def rank_from_label(label: str) -> str:
    """Return the model value for a rank label string (e.g. 'Lieutenant' -> 'lieutenant').
    Falls back to PRIVATE if the label is unrecognised."""
    return _RANK_LABEL_MAP.get(label.lower(), Person.Rank.PRIVATE)


def register_people(rows):
    """Upsert people from draft-batch rows.

    Each row must have 'id', 'name', 'age'.  If a 'rank' key is present its
    value is used directly (the /draft endpoint sends the final rank); the
    Soldier row is also created/ensured here so a separate draft_batch task
    is not strictly needed, but we keep it for idempotency.
    Returns the list of ids.
    """
    ids = []
    for p in rows:
        defaults = {"name": p["name"], "age": p["age"]}
        if "rank" in p and p["rank"]:
            defaults["rank"] = rank_from_label(p["rank"])
        Person.objects.update_or_create(id=p["id"], defaults=defaults)
        ids.append(p["id"])
    return ids


def draft_people(ids):
    """Ensure each Person in ids has a Soldier row. Idempotent."""
    with transaction.atomic():
        for person in Person.objects.filter(id__in=ids):
            Soldier.objects.get_or_create(person=person)
    return len(ids)


def load_people(payload):
    """payload: parsed people.json. Registers and drafts everyone (synchronous path)."""
    ids = register_people(payload["data"])
    draft_people(ids)
    return len(ids)


def _pick(d, *names):
    for n in names:
        if n in d:
            return d[n]
    raise KeyError(f"none of {names} in {d}")


def load_fights(payload):
    """Accept a fight-batch payload and persist any new fights + events.

    Returns a list of newly-created fight IDs (skips already-existing fights).

    Supported fight shapes – the actual /fight/* API uses:
      {blue_soldier_id, red_soldier_id, fight_id, steps: [{attacker, damage, defender}]}

    Legacy / seed shapes also accepted:
      {id, soldiers: [a, b], events: [{attacker, defender, damage}]}
      {id, fighters: [a, b], events: [...]}
      {id, soldier1/soldier_a/a, soldier2/soldier_b/b, events: [...]}
    """
    fights = payload["data"] if isinstance(payload, dict) else payload
    new_ids = []
    with transaction.atomic():
        for idx, f in enumerate(fights):
            # ── soldier IDs ──────────────────────────────────────────────────
            if "blue_soldier_id" in f or "red_soldier_id" in f:
                a = f["blue_soldier_id"]
                b = f["red_soldier_id"]
            elif "soldiers" in f:
                a, b = f["soldiers"][:2]
            elif "fighters" in f:
                a, b = f["fighters"][:2]
            else:
                a = _pick(f, "soldier1", "soldier_1", "soldier_a", "a")
                b = _pick(f, "soldier2", "soldier_2", "soldier_b", "b")

            # ── fight id ─────────────────────────────────────────────────────
            # actual API uses fight_id; fallback to id then sequential index
            fid = f.get("fight_id", f.get("id", idx))

            fight, was_new = Fight.objects.get_or_create(
                id=fid, defaults={"soldier_a_id": a, "soldier_b_id": b}
            )
            if not was_new:
                continue

            # ── events/steps ─────────────────────────────────────────────────
            # actual API uses "steps"; legacy uses "events"
            raw_events = f.get("steps", f.get("events", []))
            FightEvent.objects.bulk_create(
                FightEvent(
                    fight=fight,
                    sequence=i,
                    attacker_id=_pick(e, "attacker", "attacker_id", "from"),
                    defender_id=_pick(e, "defender", "defender_id", "to"),
                    damage=_pick(e, "damage", "dmg", "amount"),
                )
                for i, e in enumerate(raw_events)
            )
            new_ids.append(fid)
    return new_ids


def claim_fight(fight_id):
    """Atomically move pending/failed -> running. Only one worker can win."""
    return Fight.objects.filter(id=fight_id, status__in=[Fight.PENDING, Fight.FAILED]).update(
        status=Fight.RUNNING, started_at=timezone.now(), finished_at=None, error=""
    ) == 1


def apply_event(event_id):
    """Apply one hit. Atomic + idempotent. Lock order is irrelevant because a
    single event touches exactly one soldier row."""
    with transaction.atomic():  # IMMEDIATE on sqlite; select_for_update on real DBs
        ev = FightEvent.objects.select_for_update().get(pk=event_id)
        if ev.applied:
            return ev
        soldier = Soldier.objects.select_for_update().get(pk=ev.defender_id)
        new_health = max(0, soldier.health - ev.damage)
        # F()-expression keeps the write relative even if the lock were absent
        Soldier.objects.filter(pk=soldier.pk).update(health=Greatest(F("health") - ev.damage, Value(0)))
        ev.applied = True
        ev.defender_health_after = new_health
        ev.applied_at = timezone.now()
        ev.save(update_fields=["applied", "defender_health_after", "applied_at"])
        return ev


def simulate_fight(fight_id):
    if not claim_fight(fight_id):
        return "skipped"
    try:
        for eid in FightEvent.objects.filter(fight_id=fight_id, applied=False).order_by("sequence").values_list("pk", flat=True):
            apply_event(eid)
        Fight.objects.filter(pk=fight_id).update(status=Fight.DONE, finished_at=timezone.now())
        return "done"
    except Exception as exc:  # leave a trace, allow a retry
        Fight.objects.filter(pk=fight_id).update(status=Fight.FAILED, error=repr(exc), finished_at=timezone.now())
        raise


def reset_all():
    with transaction.atomic():
        FightEvent.objects.update(applied=False, defender_health_after=None, applied_at=None)
        Fight.objects.update(status=Fight.PENDING, started_at=None, finished_at=None, error="")
        Soldier.objects.update(health=MAX_HEALTH)
