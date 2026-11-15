from django.core.management.base import BaseCommand

from units.models import Unit

DEMO = [
    ("Sir Lancelot", "knight", "blue", 100, 38), ("Iron Duke", "cannon", "blue", 100, 50),
    ("Swift Hawk", "cavalry", "blue", 100, 28), ("Private Pike", "infantry", "blue", 100, 15),
    ("Black Baron", "knight", "red", 100, 40), ("Doom Mortar", "cannon", "red", 100, 45),
    ("Raven Rider", "cavalry", "red", 100, 30), ("Grunt Gus", "infantry", "red", 100, 12),
]


class Command(BaseCommand):
    help = "Create a few demo units"

    def handle(self, *a, **kw):
        for name, type_, team, hp, atk in DEMO:
            Unit.objects.get_or_create(name=name, defaults=dict(
                type=type_, team=team, health=hp, attack_points=atk,
                profile_image_link=f"https://api.dicebear.com/9.x/adventurer/png?size=100&seed={name.replace(' ', '')}",
            ))
        self.stdout.write(f"{Unit.objects.count()} units")
