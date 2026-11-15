from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Unit, Fight, FightStep
from .forms import UnitForm


class UnitModelAndFormTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'name': 'Lancelot',
            'unit_type': 'Knight',
            'team': 'Blue',
            'health': 100,
            'attack_points': 35,
            'profile_image_link': 'https://example.com/lancelot.jpg',
        }

    def test_unit_creation_valid(self):
        unit = Unit.objects.create(**self.valid_data)
        unit.full_clean()
        self.assertEqual(unit.name, 'Lancelot')
        self.assertEqual(unit.health, 100)
        self.assertEqual(unit.attack_points, 35)

    def test_unit_name_cannot_be_empty(self):
        unit = Unit(
            name='   ',
            unit_type='Infantry',
            team='Red',
            health=100,
            attack_points=20,
            profile_image_link='https://example.com/inf.jpg'
        )
        with self.assertRaises(ValidationError):
            unit.full_clean()

    def test_unit_health_boundaries(self):
        # Health > 100
        unit_high = Unit(
            name='Tank',
            unit_type='Cannon',
            team='Blue',
            health=101,
            attack_points=20,
            profile_image_link='https://example.com/tank.jpg'
        )
        with self.assertRaises(ValidationError):
            unit_high.full_clean()

        # Health < 0
        unit_low = Unit(
            name='Ghost',
            unit_type='Cannon',
            team='Blue',
            health=-1,
            attack_points=20,
            profile_image_link='https://example.com/ghost.jpg'
        )
        with self.assertRaises(ValidationError):
            unit_low.full_clean()

    def test_unit_attack_points_boundaries(self):
        # Attack points > 50
        unit = Unit(
            name='Overpowered',
            unit_type='Knight',
            team='Red',
            health=100,
            attack_points=51,
            profile_image_link='https://example.com/op.jpg'
        )
        with self.assertRaises(ValidationError):
            unit.full_clean()

        # Attack points < 0
        unit_neg = Unit(
            name='Pacifist',
            unit_type='Knight',
            team='Red',
            health=100,
            attack_points=-1,
            profile_image_link='https://example.com/pacifist.jpg'
        )
        with self.assertRaises(ValidationError):
            unit_neg.full_clean()

    def test_form_validation_valid(self):
        form = UnitForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        unit = form.save()
        self.assertEqual(unit.name, 'Lancelot')

    def test_form_validation_invalid_name(self):
        data = self.valid_data.copy()
        data['name'] = '   '
        form = UnitForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_form_validation_invalid_attack(self):
        data = self.valid_data.copy()
        data['attack_points'] = 55
        form = UnitForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('attack_points', form.errors)


class UnitViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.blue_unit = Unit.objects.create(
            name='Arthur',
            unit_type='Knight',
            team='Blue',
            health=100,
            attack_points=25,
            profile_image_link='https://example.com/arthur.jpg'
        )
        self.red_unit = Unit.objects.create(
            name='Mordred',
            unit_type='Cavalry',
            team='Red',
            health=100,
            attack_points=20,
            profile_image_link='https://example.com/mordred.jpg'
        )

    def test_unit_create_get(self):
        response = self.client.get(reverse('unit_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'war_simulator/unit_form.html')
        self.assertContains(response, 'Add')

    def test_unit_create_post_valid(self):
        data = {
            'name': 'Galahad',
            'unit_type': 'Knight',
            'team': 'Blue',
            'health': 100,
            'attack_points': 30,
            'profile_image_link': 'https://example.com/galahad.jpg'
        }
        response = self.client.post(reverse('unit_create'), data=data)
        self.assertRedirects(response, reverse('unit_all'))
        self.assertTrue(Unit.objects.filter(name='Galahad').exists())

    def test_unit_create_post_invalid(self):
        data = {
            'name': '',
            'unit_type': 'Knight',
            'team': 'Blue',
            'health': 100,
            'attack_points': 30,
            'profile_image_link': 'https://example.com/galahad.jpg'
        }
        response = self.client.post(reverse('unit_create'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'name', 'This field is required.')

    def test_unit_all_rendering(self):
        response = self.client.get(reverse('unit_all'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'war_simulator/unit_all.html')
        self.assertContains(response, 'Arthur')
        self.assertContains(response, 'Mordred')
        # Check strict 50x50 resolution
        self.assertContains(response, 'width: 50px; height: 50px; object-fit: cover;')
        # Both units are at 100 HP, so no Heal button should be rendered yet
        self.assertNotContains(response, 'onclick="healFighter')

    def test_healing_under_100_hp_unit(self):
        self.blue_unit.health = 45
        self.blue_unit.save()

        # Check that Heal button now appears
        response = self.client.get(reverse('unit_all'))
        self.assertContains(response, 'Heal')

        # Perform heal via unit_heal endpoint
        heal_url = reverse('unit_heal', args=[self.blue_unit.id])
        heal_response = self.client.post(heal_url, {'next': reverse('unit_all')})
        self.assertRedirects(heal_response, reverse('unit_all'))

        self.blue_unit.refresh_from_db()
        self.assertEqual(self.blue_unit.health, 100)

    def test_healing_via_unit_all_post(self):
        self.red_unit.health = 20
        self.red_unit.save()

        response = self.client.post(reverse('unit_all'), {
            'action': 'heal',
            'unit_id': self.red_unit.id,
        })
        self.assertRedirects(response, reverse('unit_all'))
        self.red_unit.refresh_from_db()
        self.assertEqual(self.red_unit.health, 100)

    def test_fight_simulation_same_team_fails(self):
        another_blue = Unit.objects.create(
            name='Bedivere',
            unit_type='Infantry',
            team='Blue',
            health=100,
            attack_points=15,
            profile_image_link='https://example.com/bedivere.jpg'
        )
        response = self.client.post(reverse('unit_all'), {
            'action': 'simulate',
            'fighter_ids': [self.blue_unit.id, another_blue.id]
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fighters must belong to different teams (Blue vs Red).")
        self.assertEqual(Fight.objects.count(), 0)

    def test_fight_simulation_zero_health_fails(self):
        self.blue_unit.health = 0
        self.blue_unit.save()

        response = self.client.post(reverse('unit_all'), {
            'action': 'simulate',
            'fighter_ids': [self.blue_unit.id, self.red_unit.id]
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Both fighters must have health greater than 0.")
        self.assertEqual(Fight.objects.count(), 0)

    def test_fight_simulation_distinct_fighters_validation(self):
        response = self.client.post(reverse('unit_all'), {
            'action': 'simulate',
            'fighter_ids': [self.blue_unit.id, self.blue_unit.id]
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fighters must be distinct.")

    def test_fight_simulation_cross_team_success_and_steps_persistence(self):
        response = self.client.post(reverse('unit_all'), {
            'action': 'simulate',
            'fighter_ids': [self.blue_unit.id, self.red_unit.id]
        })
        self.assertRedirects(response, reverse('unit_all'))

        # Check fight was created
        self.assertEqual(Fight.objects.count(), 1)
        fight = Fight.objects.first()
        self.assertEqual(fight.fighter_1, self.blue_unit)
        self.assertEqual(fight.fighter_2, self.red_unit)
        self.assertIsNotNone(fight.winner)

        # Check steps were persisted
        steps = FightStep.objects.filter(fight=fight).order_by('step_number')
        self.assertGreater(steps.count(), 0)

        # Check step details
        for step in steps:
            self.assertIn(step.attacker, [self.blue_unit, self.red_unit])
            self.assertIn(step.defender, [self.blue_unit, self.red_unit])
            self.assertGreaterEqual(step.damage, 0)
            self.assertLessEqual(step.damage, step.attacker.attack_points)

        # One of the fighters must have reached 0 health
        self.blue_unit.refresh_from_db()
        self.red_unit.refresh_from_db()
        self.assertTrue(self.blue_unit.health == 0 or self.red_unit.health == 0)
        self.assertIn(fight.winner, [self.blue_unit, self.red_unit])
        self.assertGreater(fight.winner.health, 0)

    def test_team_statistics_aggregation(self):
        # Create a fight with known steps
        fight = Fight.objects.create(fighter_1=self.blue_unit, fighter_2=self.red_unit)
        FightStep.objects.create(
            fight=fight,
            step_number=1,
            attacker=self.blue_unit,
            defender=self.red_unit,
            damage=25,
            attacker_health_after=100,
            defender_health_after=75
        )
        FightStep.objects.create(
            fight=fight,
            step_number=2,
            attacker=self.red_unit,
            defender=self.blue_unit,
            damage=15,
            attacker_health_after=75,
            defender_health_after=85
        )

        response = self.client.get(reverse('unit_all'))
        self.assertEqual(response.status_code, 200)
        team_stats = response.context['team_stats']

        # Blue team stats
        self.assertEqual(team_stats['Blue']['fights'], 1)
        self.assertEqual(team_stats['Blue']['damage_caused'], 25)
        self.assertEqual(team_stats['Blue']['damage_taken'], 15)

        # Red team stats
        self.assertEqual(team_stats['Red']['fights'], 1)
        self.assertEqual(team_stats['Red']['damage_caused'], 15)
        self.assertEqual(team_stats['Red']['damage_taken'], 25)

    def test_unit_detail_view(self):
        fight = Fight.objects.create(
            fighter_1=self.blue_unit,
            fighter_2=self.red_unit,
            winner=self.blue_unit
        )
        step = FightStep.objects.create(
            fight=fight,
            step_number=1,
            attacker=self.blue_unit,
            defender=self.red_unit,
            damage=30,
            attacker_health_after=100,
            defender_health_after=70
        )

        detail_url = reverse('unit_detail', args=[self.blue_unit.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'war_simulator/unit_detail.html')
        self.assertContains(response, 'Arthur')
        self.assertContains(response, 'Team Blue')
        self.assertContains(response, 'Knight')
        self.assertContains(response, f'Fight #{fight.id}')
        self.assertContains(response, 'Arthur')
        self.assertContains(response, '-30')

    def test_trailing_and_no_trailing_slash_routes(self):
        # Test /unit and /unit/
        r1 = self.client.get('/unit')
        self.assertEqual(r1.status_code, 200)
        r2 = self.client.get('/unit/')
        self.assertEqual(r2.status_code, 200)

        # Test /unit/all and /unit/all/
        r3 = self.client.get('/unit/all')
        self.assertEqual(r3.status_code, 200)
        r4 = self.client.get('/unit/all/')
        self.assertEqual(r4.status_code, 200)

        # Test /unit/<id> and /unit/<id>/
        r5 = self.client.get(f'/unit/{self.blue_unit.id}')
        self.assertEqual(r5.status_code, 200)
        r6 = self.client.get(f'/unit/{self.blue_unit.id}/')
        self.assertEqual(r6.status_code, 200)
