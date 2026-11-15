"""Make sure the Celery app is loaded when Django starts.

Importing it here means ``@shared_task`` in the apps always binds to this app.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)
