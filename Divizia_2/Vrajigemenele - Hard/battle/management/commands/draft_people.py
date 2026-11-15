from django.core.management.base import BaseCommand

from battle.tasks import download_draft_batch


class Command(BaseCommand):
    help = "Download people from /draft/* batches and register+draft them as parallel background tasks."

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
                download_draft_batch.delay(host, b)
            self.stdout.write(f"queued {batches} draft-download tasks")
        else:
            download_draft_batch.delay(host, 0)
            self.stdout.write("queued batch 0; each batch chains to the next")
