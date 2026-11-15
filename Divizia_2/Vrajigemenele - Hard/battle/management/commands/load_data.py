import json
import urllib.request

from django.core.management.base import BaseCommand

from battle import services


def _read(src):
    if src.startswith("http"):
        with urllib.request.urlopen(src) as r:
            return json.load(r)
    with open(src, encoding="utf-8") as f:
        return json.load(f)


class Command(BaseCommand):
    help = "Register people (drafting them as soldiers) and/or import fights from a file or URL."

    def add_arguments(self, p):
        p.add_argument("--people", help="path/URL of people.json")
        p.add_argument("--fights", help="path/URL of the /simulate-fight-info JSON")

    def handle(self, *a, people=None, fights=None, **kw):
        if people:
            self.stdout.write(f"people: {services.load_people(_read(people))}")
        if fights:
            self.stdout.write(f"new fights: {services.load_fights(_read(fights))}")
