from django.test import TestCase
from django.urls import reverse

from .models import Fight, FightStep, Unit


def make_unit(name="A", team="Blue", health=100, attack=20, unit_type="Knight"):
    return Unit.objects.create(
        name=name, unit_type=unit_type, team=team, health=health, attack_points=attack
    )


class UnitTests(TestCase):
    def test_create_unit(self):
        r = self.client.post(reverse("unit_create"), {
            "name": "Rex", "unit_type": "Cannon", "team": "Red",
            "health": 100, "attack_points": 30, "profile_image_link": "",
        })
        self.assertRedirects(r, reverse("unit_list"))
        self.assertEqual(Unit.objects.count(), 1)

    def test_invalid_values_show_errors(self):
        r = self.client.post(reverse("unit_create"), {
            "name": "Rex", "unit_type": "Cannon", "team": "Red",
            "health": 150, "attack_points": 99,
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Unit.objects.count(), 0)
        self.assertContains(r, "errorlist")

    def test_heal_button_and_heal(self):
        u = make_unit(health=40)
        r = self.client.get(reverse("unit_list"))
        self.assertContains(r, "Heal")
        self.client.post(reverse("unit_heal", args=[u.pk]))
        u.refresh_from_db()
        self.assertEqual(u.health, 100)
        self.assertNotContains(self.client.get(reverse("unit_list")), "Heal</button>")

    def test_detail_page(self):
        u = make_unit()
        self.assertContains(self.client.get(reverse("unit_detail", args=[u.pk])), u.name)


class FightTests(TestCase):
    def setUp(self):
        self.a = make_unit("A", "Blue")
        self.b = make_unit("B", "Red")

    def simulate(self, *units):
        return self.client.post(reverse("simulate"), {"units": [u.pk for u in units]})

    def test_fight_runs_to_the_end(self):
        r = self.simulate(self.a, self.b)
        fight = Fight.objects.get()
        self.assertRedirects(r, reverse("fight_detail", args=[fight.pk]))
        self.a.refresh_from_db(); self.b.refresh_from_db()
        self.assertEqual(sorted([self.a.health, self.b.health])[0], 0)
        self.assertEqual(fight.winner.health > 0, True)
        last = fight.steps.last()
        self.assertEqual(last.defender_health, 0)
        # attacks alternate, starting with the first selected unit
        attackers = [s.attacker_id for s in fight.steps.all()]
        self.assertEqual(attackers[0], self.a.pk)
        self.assertTrue(all(x != y for x, y in zip(attackers, attackers[1:])))

    def test_same_team_rejected(self):
        c = make_unit("C", "Blue")
        self.simulate(self.a, c)
        self.assertEqual(Fight.objects.count(), 0)

    def test_needs_exactly_two(self):
        self.simulate(self.a)
        self.assertEqual(Fight.objects.count(), 0)

    def test_dead_unit_rejected(self):
        self.b.health = 0; self.b.save()
        self.simulate(self.a, self.b)
        self.assertEqual(Fight.objects.count(), 0)

    def test_stats_and_unit_history(self):
        self.simulate(self.a, self.b)
        r = self.client.get(reverse("unit_list"))
        stats = {row["team"]: row for row in r.context["stats"]}
        self.assertEqual(stats["Blue"]["fights"], 1)
        self.assertEqual(stats["Red"]["fights"], 1)
        # damage caused by one team == damage taken by the other
        self.assertEqual(stats["Blue"]["caused"], stats["Red"]["taken"])
        self.assertEqual(stats["Red"]["caused"], stats["Blue"]["taken"])
        self.assertEqual(stats["Blue"]["caused"] + stats["Red"]["caused"], 100 + 100 - (
            Unit.objects.get(pk=self.a.pk).health + Unit.objects.get(pk=self.b.pk).health))
        detail = self.client.get(reverse("unit_detail", args=[self.a.pk]))
        self.assertContains(detail, "Winner")
        self.assertEqual(FightStep.objects.filter(fight__unit_a=self.a).exists(), True)
