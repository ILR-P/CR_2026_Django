import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hardchallenge.settings")

app = Celery("hardchallenge")
# Every setting that starts with CELERY_ in settings.py is read here.
app.config_from_object("django.conf:settings", namespace="CELERY")
# Finds tasks.py inside every installed app (people/tasks.py).
app.autodiscover_tasks()
