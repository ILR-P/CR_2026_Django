import requests
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.db.models import F, Value
from django.db.models.functions import Greatest

from .models import Fight, FightEvent, Person

BASE = settings.CHALLENGE_API_BASE_URL.rstrip('/')
retrying_task = shared_task(
    autoretry_for=(requests.RequestException,), retry_backoff=3, max_retries=5
)


def api_get(path):
    response = requests.get(f'{BASE}/{path}', timeout=settings.CHALLENGE_API_TIMEOUT)
    response.raise_for_status()
    return response.json()


def hellstorm_key(rows):
    for row in rows:
        if row.get('key'):
            return row['key']
    return None


@retrying_task
def register_people():
    rows = api_get('people')['data']
    Person.objects.bulk_create(
        [
            Person(
                external_id=r['id'], name=r['name'], age=r['age'],
                key=r.get('key', ''),
            )
            for r in rows
        ],
        update_conflicts=True,
        update_fields=['name', 'age', 'key'],
        unique_fields=['external_id'],
    )
    key = hellstorm_key(rows) 
    if key:
        follow_key.delay(key)
    return f'{len(rows)} people registered'


@retrying_task
def follow_key(key):
    print(f'[{key}] {api_get(key)["data"]["message"]}')
    if key == 'draft-info':
        download_draft.delay(0)
    elif key == 'fight-info':
        download_fights.delay(0)
    return key


@retrying_task
def download_draft(index):
    payload = api_get(f'draft/{index}')
    rows = payload['data']
    for r in rows:
        Person.objects.filter(external_id=r['id']).update(
            rank=r['rank'], health=r['health']
        )

    next_index = payload.get('next_batch')
    if next_index is not None:
        download_draft.delay(next_index)
    else:
        key = hellstorm_key(rows)
        if key:
            follow_key.delay(key)
    return f'draft/{index}: {len(rows)} drafted'


@retrying_task
def download_fights(index):
    payload = api_get(f'fight/{index}')
    rows = payload['data']
    for row in rows:
        save_fight.delay(row)

    next_index = payload.get('next_batch', payload.get('next'))
    if next_index is not None:
        download_fights.delay(next_index)
    return f'fight/{index}: {len(rows)} fights'


@shared_task
def save_fight(row):
    with transaction.atomic():
        fight, _ = Fight.objects.get_or_create(
            external_id=row['fight_id'],
            defaults={
                'blue_id': row['blue_soldier_id'],
                'red_id': row['red_soldier_id'],
            },
        )
        FightEvent.objects.bulk_create(
            [
                FightEvent(
                    fight=fight, sequence=i, attacker_id=step['attacker'],
                    defender_id=step['defender'], damage=step['damage'],
                )
                for i, step in enumerate(row['steps'])
            ],
            ignore_conflicts=True,
        )
    return f'fight {row["fight_id"]}: {len(row["steps"])} events'


@shared_task
def simulate_all():
    ids = list(Fight.objects.filter(simulated=False).values_list('external_id', flat=True))
    for external_id in ids:
        simulate_fight.delay(external_id)
    return f'{len(ids)} fights dispatched'


@shared_task
def simulate_fight(external_id):
    claimed = Fight.objects.filter(external_id=external_id, simulated=False).update(
        simulated=True
    )
    if not claimed:
        return f'fight {external_id} already simulated'

    fight = Fight.objects.get(external_id=external_id)
    for event in fight.events.order_by('sequence'):
        Person.objects.filter(external_id=event.defender_id).update(
            health=Greatest(F('health') - event.damage, Value(0))
        )
        hp_after = Person.objects.values_list('health', flat=True).get(
            external_id=event.defender_id
        )
        FightEvent.objects.filter(pk=event.pk).update(defender_health_after=hp_after)

    hp = dict(
        Person.objects.filter(
            external_id__in=[fight.blue_id, fight.red_id]
        ).values_list('external_id', 'health')
    )
    winner_id = None
    if hp[fight.blue_id] > hp[fight.red_id]:
        winner_id = fight.blue_id
    elif hp[fight.red_id] > hp[fight.blue_id]:
        winner_id = fight.red_id
    Fight.objects.filter(pk=fight.pk).update(winner_id=winner_id)
    return f'fight {external_id} simulated'


@shared_task
def reset():
    Person.objects.update(health=settings.MAX_HEALTH)
    Fight.objects.update(simulated=False, winner=None)
    FightEvent.objects.update(defender_health_after=None)
    return 'reset'
