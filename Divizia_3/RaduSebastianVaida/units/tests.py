
from django.test import TestCase
from django.urls import reverse

from .models import Unit, Fight, FightTurn


class UnitModelTests(TestCase):

    def setUp(self):
        self.blue_unit = Unit.objects.create(
            name="Blue Knight",
            type="Knight",
            team="Blue",
            health=100,
            attack_points=20
        )

        self.red_unit = Unit.objects.create(
            name="Red Cavalry",
            type="Cavalry",
            team="Red",
            health=100,
            attack_points=15
        )

    def test_unit_creation(self):
        self.assertEqual(
            self.blue_unit.name,
            "Blue Knight"
        )

        self.assertEqual(
            self.blue_unit.health,
            100
        )

    def test_unit_string_representation(self):
        self.assertEqual(
            str(self.blue_unit),
            "Blue Knight (Knight)"
        )

    def test_default_health(self):
        unit = Unit.objects.create(
            name="New Infantry",
            type="Infantry",
            team="Blue",
            attack_points=10
        )

        self.assertEqual(unit.health, 100)

    def test_heal_unit(self):
        self.blue_unit.health = 40
        self.blue_unit.save()

        self.blue_unit.heal()

        self.assertEqual(
            self.blue_unit.health,
            100
        )


class UnitViewTests(TestCase):

    def setUp(self):
        self.blue_unit = Unit.objects.create(
            name="Blue Knight",
            type="Knight",
            team="Blue",
            health=100,
            attack_points=20
        )

        self.red_unit = Unit.objects.create(
            name="Red Cavalry",
            type="Cavalry",
            team="Red",
            health=100,
            attack_points=15
        )

    def test_add_unit_page(self):
        response = self.client.get(
            reverse("add_unit")
        )

        self.assertEqual(response.status_code, 200)

    def test_all_units_page(self):
        response = self.client.get(
            reverse("all_units")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Blue Knight"
        )

    def test_unit_details_page(self):
        response = self.client.get(
            reverse(
                "unit_details",
                args=[self.blue_unit.id]
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Blue Knight"
        )

    def test_heal_unit(self):
        self.blue_unit.health = 30
        self.blue_unit.save()

        response = self.client.post(
            reverse(
                "heal_unit",
                args=[self.blue_unit.id]
            )
        )

        self.blue_unit.refresh_from_db()

        self.assertEqual(
            self.blue_unit.health,
            100
        )

        self.assertEqual(response.status_code, 302)

    def test_same_team_fight_is_rejected(self):
        response = self.client.post(
            reverse("simulate_fight"),
            {
                "unit1_id": self.blue_unit.id,
                "unit2_id": self.blue_unit.id,
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Fight.objects.count(), 0)

    def test_fight_between_different_teams(self):
        response = self.client.post(
            reverse("simulate_fight"),
            {
                "unit1_id": self.blue_unit.id,
                "unit2_id": self.red_unit.id,
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Fight.objects.count(), 1)

        fight = Fight.objects.first()

        self.assertGreater(
            fight.turns.count(),
            0
        )

        self.blue_unit.refresh_from_db()
        self.red_unit.refresh_from_db()

        self.assertTrue(
            fight.winner is not None
            or (
                self.blue_unit.health == 0
                and self.red_unit.health == 0
            )
        )
from django.test import TestCase

# Create your tests here.
