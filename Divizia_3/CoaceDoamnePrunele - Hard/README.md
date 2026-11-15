# Django War Simulator

General Deadlock's war, in four stages. Each stage is kicked off by the one
before it, by following the key Hellstorm Fireburn carries:

## Team 

Team: Coace Doamne Prunele</br>
Division: 3</br>
Members: Stoian Andrea, Trif Alexandra, Salagean Lorena

## Running it

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate

# terminal 1 — the worker
.venv/bin/celery -A coderun2026_starter worker -l info --concurrency=16 --pool=threads

# terminal 2 — the site
.venv/bin/python manage.py runserver
```

Then open <http://127.0.0.1:8000/> and press **Run the pipeline** (stages 1–3,
a few minutes: the API answers in ~11s per request). When the fights are in,
go to **/simulate** and press **Simulate all fights**.

## Pages

- `/` — the register: everyone, with rank and a health bar
- `/fights/` — every downloaded fight
- `/fights/<id>/` — one fight's full event log, with health after each hit
- `/simulate/` — run the parallel simulation and see the results
- `/admin/` — the raw tables
