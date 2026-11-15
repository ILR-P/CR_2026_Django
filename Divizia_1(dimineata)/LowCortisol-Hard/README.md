# Hard challenge

Setup (run inside this folder):

    pip install -r requirements.txt
    python manage.py makemigrations people
    python manage.py migrate

Terminal 1 (worker, 8 tasks at the same time):

    celery -A hardchallenge worker --pool=threads --concurrency=8 -l info

Terminal 2:

    python manage.py start_draft
    python manage.py runserver

Open http://127.0.0.1:8000/status to see the people and their ranks.
