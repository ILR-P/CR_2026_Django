import json
import random

from django.core.management.base import BaseCommand

from battle import services
from battle.models import Soldier


class Command(BaseCommand):
    help = "Generate random demo fights (for when /simulate-fight-info data isn't available)."

    def add_arguments(self, p):
        p.add_argument("--fights", type=int, default=40)
        p.add_argument("--seed", type=int, default=1)
        p.add_argument("--dump", help="also write the generated JSON here")

    def handle(self, *a, fights, seed, dump, **kw):
        rnd = random.Random(seed)
        ids = list(Soldier.objects.values_list("pk", flat=True))
        data = []
        for i in range(fights):
            a, b = rnd.sample(ids, 2)
            events = []
            for _ in range(rnd.randint(3, 12)):
                att, dfn = rnd.choice([(a, b), (b, a)])
                events.append({"attacker": att, "defender": dfn, "damage": rnd.randint(1, 15)})
            data.append({"id": i, "soldiers": [a, b], "events": events})
        if dump:
            json.dump({"data": data}, open(dump, "w"), indent=2)
        self.stdout.write(f"new fights: {services.load_fights(data)}")
