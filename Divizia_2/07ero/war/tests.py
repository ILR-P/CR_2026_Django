import random

from django.test import TestCase
from django.urls import reverse

from .models import Fight, FightStep, Unit
from .services import FightError, simulate_fight, team_statistics


def make(name="A", team="Blue", attack=20, health=100, type="Knight"):
    return Unit.objects.create(name=name, type=type, team=team, attack_points=attack, health=health)


class FormTests(TestCase):
    def test_form_page_and_create(self):
        self.assertEqual(self.client.get("/unit").status_code, 200)
        r = self.client.post("/unit", {"name": "Bob", "type": "Cannon", "team": "Red",
                                        "health": 100, "attack_points": 30, "profile_image_link": ""})
        self.assertRedirects(r, "/unit/all")
        self.assertEqual(Unit.objects.get().name, "Bob")

    def test_validation_errors_are_shown(self):
        r = self.client.post("/unit", {"name": "", "type": "Dragon", "team": "Green",
                                        "health": 101, "attack_points": 51})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Unit.objects.count(), 0)
        for f in ("name", "type", "team", "health", "attack_points"):
            self.assertIn(f, r.context["form"].errors)
        self.assertContains(r, "errorlist")


class ListTests(TestCase):
    def test_list_heal_and_detail(self):
        full, hurt = make("Full"), make("Hurt", team="Red", health=40)
        r = self.client.get("/unit/all")
        self.assertContains(r, "Full"); self.assertContains(r, "Hurt")
        self.assertContains(r, 'width="50" height="50"')
        self.assertEqual(r.content.decode().count(">Heal</button>"), 1)
        self.assertContains(r, f'href="/unit/{full.pk}"')
        self.client.post(f"/unit/{hurt.pk}/heal")
        hurt.refresh_from_db(); self.assertEqual(hurt.health, 100)
        d = self.client.get(f"/unit/{full.pk}")
        self.assertContains(d, "Full"); self.assertContains(d, "Attack points")
        self.assertEqual(self.client.get("/unit/999").status_code, 404)

    def test_heal_requires_post(self):
        u = make(health=10)
        self.assertEqual(self.client.get(f"/unit/{u.pk}/heal").status_code, 405)


class FightTests(TestCase):
    def test_simulation_rules(self):
        a, b = make("A", "Blue"), make("B", "Red", attack=15)
        fight = simulate_fight(a, b, rng=random.Random(1))
        a.refresh_from_db(); b.refresh_from_db()
        self.assertEqual(sorted([a.health > 0, b.health > 0]), [False, True])
        self.assertEqual(fight.winner, a if a.health > 0 else b)
        steps = list(fight.steps.all())
        self.assertEqual(steps[0].attacker, a)
        for prev, cur in zip(steps, steps[1:]):
            self.assertNotEqual(prev.attacker, cur.attacker)
        self.assertTrue(all(0 <= s.damage <= s.attacker.attack_points for s in steps))
        self.assertEqual(steps[-1].defender_health, 0)

    def test_rejections(self):
        a, b, c = make("A"), make("B", "Red"), make("C")
        for x, y in ((a, a), (a, c)):
            with self.assertRaises(FightError): simulate_fight(x, y)
        b.health = 0
        with self.assertRaises(FightError): simulate_fight(a, b)
        z1, z2 = make("Z1", attack=0), make("Z2", "Red", attack=0)
        with self.assertRaises(FightError): simulate_fight(z1, z2)

    def test_view_and_stats(self):
        a, b = make("A"), make("B", "Red")
        r = self.client.post("/unit/simulate", {"fighters": [a.pk, b.pk]}, follow=True)
        self.assertRedirects(r, "/unit/all")
        self.assertEqual(Fight.objects.count(), 1)
        total = sum(s.damage for s in FightStep.objects.all())
        stats = {s["team"]: s for s in team_statistics()}
        self.assertEqual(stats["Blue"]["fights"], 1); self.assertEqual(stats["Red"]["fights"], 1)
        self.assertEqual(stats["Blue"]["damage_caused"] + stats["Red"]["damage_caused"], total)
        self.assertEqual(stats["Blue"]["damage_caused"], stats["Red"]["damage_taken"])
        self.assertContains(r, "Damage caused")
        self.assertContains(self.client.get(f"/unit/{a.pk}"), "winner:")

    def test_view_errors(self):
        a, c = make("A"), make("C")
        for data in ({"fighters": [a.pk]}, {"fighters": [a.pk, c.pk]}, {}):
            r = self.client.post("/unit/simulate", data, follow=True)
            self.assertContains(r, "error")
        self.assertEqual(Fight.objects.count(), 0)
