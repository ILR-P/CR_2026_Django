"""Celery application bootstrap.

The starter project ships Celery *settings* but no Celery *app*, so this module
creates it and wires it to Django. Everything prefixed with ``CELERY_`` in
``settings.py`` becomes Celery configuration.
"""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coderun2026_starter.settings')

app = Celery('coderun2026_starter')

# Pull configuration from Django settings, looking at the CELERY_ namespace.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks.py in every installed app.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Smoke-test task: ``celery -A coderun2026_starter call ...debug_task``."""
    print(f'Request: {self.request!r}')
