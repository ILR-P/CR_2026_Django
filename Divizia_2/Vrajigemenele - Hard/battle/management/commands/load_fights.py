from django.core.management.base import BaseCommand

from battle.tasks import download_fight_batch


class Command(BaseCommand):
    help = "Download fight batches from /fight/* and queue simulate tasks, as parallel background tasks."

    def add_arguments(self, p):
        p.add_argument("--host", required=True, help="e.g. https://host.example")
        p.add_argument(
            "--batches",
            type=int,
            help="if you know the batch count, kick off all batches at once; "
                 "otherwise leave blank and each batch will chain to the next",
        )

    def handle(self, *a, host, batches, **kw):
        if batches:
            for b in range(batches):
                download_fight_batch.delay(host, b)
            self.stdout.write(f"queued {batches} fight-download tasks")
        else:
            download_fight_batch.delay(host, 0)
            self.stdout.write("queued batch 0; each batch chains to the next")
