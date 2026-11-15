"""Celery tasks for the battle app.

Draft pipeline
--------------
  download_draft_batch(host, batch_index)
    -> registers people from /draft/<batch_index>
    -> creates Soldier rows via draft_batch(ids)
    -> if next_batch is not None: schedules download_draft_batch(host, next_batch)

Fight pipeline
--------------
  download_fight_batch(host, batch_index)
    -> loads fights from /fight/<batch_index> into the DB
    -> if next_batch is not None: schedules download_fight_batch(host, next_batch)
    -> for each NEW fight, schedules simulate_fight(fight_id)

simulate_fight(fight_id)
    -> applies every event in sequence (atomic + idempotent per event)
"""
import requests
from celery import shared_task
from django.conf import settings

from . import services

# Transient failures worth retrying: the host is slow ("a batch might time out").
RETRYABLE = (requests.Timeout, requests.ConnectionError, requests.HTTPError)


# ---------------------------------------------------------------------------
# Draft download
# ---------------------------------------------------------------------------

@shared_task(
    bind=True,
    name="battle.download_draft_batch",
    autoretry_for=RETRYABLE,
    retry_backoff=2,          # 2s, 4s, 8s … between attempts
    retry_backoff_max=60,
    retry_jitter=True,        # so retried batches don't all hit the host at once
    max_retries=8,
    acks_late=True,           # a crashed worker doesn't lose the batch
)
def download_draft_batch(self, host, batch_index):
    """Download one /draft/<batch_index> batch, register+draft the people, then
    immediately chain to the next batch if the response says there is one."""
    url = host.rstrip("/") + "/draft/" + str(batch_index)
    resp = requests.get(url, timeout=settings.DRAFT_REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    rows = data.get("data") or []

    if rows:
        ids = services.register_people(rows)   # rank comes directly from the API
        draft_batch.delay(ids)                 # each batch = its own task call

    next_b = data.get("next_batch")
    if next_b is not None and next_b != batch_index:
        download_draft_batch.delay(host, next_b)

    return {"batch": batch_index, "people": len(rows), "next_batch": next_b}


@shared_task(
    bind=True,
    name="battle.draft_batch",
    autoretry_for=(Exception,),
    retry_backoff=1,
    retry_backoff_max=30,
    retry_jitter=True,
    max_retries=5,
)
def draft_batch(self, person_ids):
    """Ensure each person in person_ids has a Soldier row."""
    return services.draft_people(person_ids)


# ---------------------------------------------------------------------------
# Fight download
# ---------------------------------------------------------------------------

@shared_task(
    bind=True,
    name="battle.download_fight_batch",
    autoretry_for=RETRYABLE,
    retry_backoff=2,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=8,
    acks_late=True,
)
def download_fight_batch(self, host, batch_index):
    """Download one /fight/<batch_index> batch, persist fights+events, then
    launch a simulate_fight task for each NEW fight and chain to the next batch."""
    url = host.rstrip("/") + "/fight/" + str(batch_index)
    resp = requests.get(url, timeout=settings.FIGHT_REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    # load_fights returns the list of newly-created fight IDs
    new_fight_ids = services.load_fights(data)

    # Schedule a simulate task for each fight that was just created (parallel)
    for fid in new_fight_ids:
        simulate_fight.delay(fid)

    next_b = data.get("next_batch")
    if next_b is not None and next_b != batch_index:
        download_fight_batch.delay(host, next_b)

    return {"batch": batch_index, "new_fights": len(new_fight_ids), "next_batch": next_b}


# ---------------------------------------------------------------------------
# Fight simulation
# ---------------------------------------------------------------------------

@shared_task(
    bind=True,
    name="battle.simulate_fight",
    autoretry_for=(Exception,),
    retry_backoff=1,
    retry_backoff_max=30,
    retry_jitter=True,
    max_retries=3,
)
def simulate_fight(self, fight_id):
    return services.simulate_fight(fight_id)
