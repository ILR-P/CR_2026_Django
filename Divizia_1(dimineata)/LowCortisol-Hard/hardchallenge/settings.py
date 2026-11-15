import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "dev-only-secret-key-change-me"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "people",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "hardchallenge.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        # Several workers write at the same time, so wait instead of failing.
        "OPTIONS": {"timeout": 30},
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True

# ---------- Challenge host ----------
DRAFT_HOST = os.environ.get(
    "DRAFT_HOST",
    "https://coderun2026-csbwf4haa4d0gubu.westus3-01.azurewebsites.net",
)
# The server is slow on purpose, so give every request a long time.
REQUEST_TIMEOUT_SECONDS = 60
# How many people go into one drafting batch (= one background task each).
BATCH_SIZE = 10

# ---------- Celery ----------
# SQLite file as broker: works on Windows with no Redis install.
# For Redis instead, set CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_BROKER_URL = os.environ.get(
    "CELERY_BROKER_URL", "sqla+sqlite:///celery-broker.sqlite3"
)
CELERY_TASK_IGNORE_RESULT = True
