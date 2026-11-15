# Django War Simulator

```
pip install django celery sqlalchemy requests
python manage.py migrate
celery -A coderun2026_starter worker -P threads -c 16 -l info     # terminal 1 (background tasks)
python manage.py runserver                                         # terminal 2
```

## Easy  (units app)
- `/unit` add a unit (form with validation) · `/unit/all` cards, Heal, pick two + Simulate, team stats · `/unit/<id>` details + fight history cards
- `python manage.py seed_units` creates demo units

## Hard  (battle app)

The challenge host is `https://coderun2026-csbwf4haa4d0gubu.westus3-01.azurewebsites.net`.

### Step 1 – Draft people

Downloads `/draft/0`, `/draft/1` … following `next_batch` until `null`.
Each batch is a separate background task; rank comes directly from the API.

```
python manage.py draft_people --host https://coderun2026-csbwf4haa4d0gubu.westus3-01.azurewebsites.net
```

Offline alternative (uses local people.json, derives rank from age):
```
python manage.py load_data --people people.json
```

### Step 2 – Load fights + simulate

Downloads `/fight/0`, `/fight/1` … following `next_batch`, saves fight events to DB,
then kicks off a `simulate_fight` task per fight — all in parallel.

```
python manage.py load_fights --host https://coderun2026-csbwf4haa4d0gubu.westus3-01.azurewebsites.net
```

Or from the `/simulate` page UI: enter the host URL and click "Load & simulate fights".

### Step 3 – View results at `/simulate`

- Each fight is a background Celery task (parallel).
- Page auto-refreshes every 2 s while tasks are running.
- Shows fight events, final soldier health bars.
- "Reset health & replay all fights" button for re-running.

## Concurrency notes

- SQLite is opened with `IMMEDIATE` transaction mode so concurrent workers
  serialise writes (no "database is locked" errors).
- `claim_fight()` atomically moves `pending → running`; a double-launch or retry
  is harmless.
- `apply_event()` uses `SELECT FOR UPDATE` + an F()-expression; a re-applied
  event is a no-op.
- Draft and fight download tasks each have retry policies (backoff, jitter) to
  handle the host's timeouts.
