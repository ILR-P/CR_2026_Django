import json
import time
import urllib.request

from django.core.management.base import BaseCommand
from army.models import Person

HOST = "https://coderun2026-csbwf4haa4d0gubu.westus3-01.azurewebsites.net"


class Command(BaseCommand):
    help = "Descarcă oamenii de la /people și îi salvează în DB"

    def handle(self, *args, **opts):
        d = None
        for attempt in range(1, 6):
            self.stdout.write(f"încercarea {attempt}: cer /people (max 60s)...")
            t = time.time()
            try:
                with urllib.request.urlopen(f"{HOST}/people", timeout=60) as r:
                    d = json.loads(r.read().decode("utf-8"))
                self.stdout.write(f"  răspuns în {time.time() - t:.1f}s")
                break
            except Exception as e:
                self.stdout.write(f"  eșec după {time.time() - t:.1f}s: {e!r}")

        if d is None:
            self.stderr.write("Serverul nu a răspuns. Salvează /people din browser ca people_raw.json.")
            return

        with open("people_raw.json", "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

        self.stdout.write(f"chei de sus: {list(d.keys())}")
        people = d["data"]
        Person.objects.bulk_create(
            [Person(external_id=p["id"], name=p["name"], age=p.get("age"), extra=p)
             for p in people],
            ignore_conflicts=True,
        )
        self.stdout.write(f"salvat {len(people)}; total în DB: {Person.objects.count()}")