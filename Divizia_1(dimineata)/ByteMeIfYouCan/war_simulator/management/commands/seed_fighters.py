from django.core.management.base import BaseCommand
from war_simulator.models import Unit


class Command(BaseCommand):
    help = 'Seeds initial fighters for Blue and Red teams'

    def handle(self, *args, **options):
        initial_units = [
            {
                'name': 'Conor McGregor',
                'unit_type': 'Knight',
                'team': 'Blue',
                'health': 100,
                'attack_points': 35,
                'profile_image_link': 'https://media.sportsnaut.com/wp-content/uploads/2025/09/Conor-McGregor-USA-TODAY-Sports-788x591.jpg',
            },
            {
                'name': 'Daniel Cormier',
                'unit_type': 'Cannon',
                'team': 'Blue',
                'health': 100,
                'attack_points': 45,
                'profile_image_link': 'https://media.sportsnaut.com/wp-content/uploads/2025/09/Daniel-Cormier-USA-TODAY-Sports-788x591.jpg',
            },
            {
                'name': 'Kamaru Usman',
                'unit_type': 'Infantry',
                'team': 'Blue',
                'health': 100,
                'attack_points': 22,
                'profile_image_link': 'https://media.sportsnaut.com/wp-content/uploads/2025/09/Kamaru-Usman-USA-TODAY-Sports-788x591.jpg',
            },
            {
                'name': 'Fedor Emelianenko',
                'unit_type': 'Knight',
                'team': 'Red',
                'health': 100,
                'attack_points': 38,
                'profile_image_link': 'https://media.sportsnaut.com/wp-content/uploads/2025/09/Fedor-Emelianenko-USA-TODAY-Sports-788x591.jpg',
            },
            {
                'name': 'Khabib Nurmagomedov',
                'unit_type': 'Cavalry',
                'team': 'Red',
                'health': 100,
                'attack_points': 30,
                'profile_image_link': 'https://media.sportsnaut.com/wp-content/uploads/2025/09/Khabib-Nurmagomedov-USA-TODAY-Sports-788x591.jpg',
            },
            {
                'name': 'Anderson Silva',
                'unit_type': 'Cannon',
                'team': 'Red',
                'health': 100,
                'attack_points': 48,
                'profile_image_link': 'https://media.sportsnaut.com/wp-content/uploads/2025/09/Anderson-Silva-USA-TODAY-Sports-788x591.jpg',
            },
        ]

        count = 0
        for data in initial_units:
            unit, created = Unit.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} new fighters."))
