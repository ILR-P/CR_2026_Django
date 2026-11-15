import requests
from celery import shared_task
from django.conf import settings

from .models import Person

# If a request fails (timeout or server error), Celery runs the task again:
# waits 1s, 2s, 4s... (retry_backoff), at most 20s, at most 40 retries.
# The challenge server is overloaded, so we are very patient.
RETRY_POLICY = {
    "autoretry_for": (requests.RequestException,),
    "retry_backoff": True,
    "retry_backoff_max": 20,
    "retry_jitter": True,
    "max_retries": 40,
}

# (connect timeout, read timeout) in seconds. A request we give up on is
# still processed by the server, so we wait long instead of sending many.
REQUEST_TIMEOUT = (10, 300)


def fetch_json(path):
    url = settings.DRAFT_HOST + path
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


@shared_task(**RETRY_POLICY)
def download_people():
    """Download the list, save it, and start one drafting task per batch."""
    people = fetch_json("/people")["data"]
    batch_size = settings.BATCH_SIZE

    for start in range(0, len(people), batch_size):
        batch = people[start:start + batch_size]

        saved_ids = []
        for person_data in batch:
            Person.objects.update_or_create(
                id=person_data["id"],
                defaults={"name": person_data["name"], "age": person_data["age"]},
            )
            saved_ids.append(person_data["id"])

        # This batch is saved, so its drafting can start right now,
        # while the next batches are still being saved.
        draft_batch.delay(saved_ids)


def compute_rank(person):
    # PLACEHOLDER rule: the real rule from the challenge is not known yet.
    # Replace this function once the rank rule is found.
    return person.age


@shared_task(**RETRY_POLICY)
def draft_batch(person_ids):
    """Draft one batch: give a rank to each person in it."""
    for person in Person.objects.filter(id__in=person_ids):
        person.rank = compute_rank(person)
        person.save(update_fields=["rank"])
