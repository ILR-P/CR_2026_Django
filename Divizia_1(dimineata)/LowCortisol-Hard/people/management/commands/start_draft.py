from django.core.management.base import BaseCommand

from people.tasks import download_people


class Command(BaseCommand):
    help = "Queue the background task that downloads and drafts all the people."

    def handle(self, *args, **options):
        download_people.delay()
        self.stdout.write("download_people queued. Watch the Celery worker window.")
