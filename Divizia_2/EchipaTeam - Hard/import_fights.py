import os
import json
import urllib.request
import django

# Inițializăm mediul Django pentru a folosi baza de date
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coderun2026_starter.settings')
django.setup()

from army.models import Fight, FightEvent
from django.db import transaction

HOST = "https://coderun2026-csbwf4haa4d0gubu.westus3-01.azurewebsites.net"
current_path = "/fight/0"  # Aici zice serverul să începem
total_importate = 0

print("Încep descărcarea luptelor în batch-uri...")

while current_path:
    print(f"-> Procesez lotul de la: {current_path}")
    url = f"{HOST}{current_path}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Eroare la descărcare: {e}")
        break

    # Extragem luptele
    fights = data.get('data', [])
    if isinstance(fights, dict) and 'fights' in fights:
        fights = fights['fights']
    elif 'fights' in data:
        fights = data['fights']
    elif isinstance(data, list):
        fights = data

    if fights:
        # Iterăm prin fiecare luptă și o salvăm
        for f in fights:
            with transaction.atomic():
                # Extragem datele cu noile chei descoperite
                fight, created = Fight.objects.get_or_create(
                    external_id=str(f.get('fight_id')),
                    defaults={
                        'soldier_a_id': f['blue_soldier_id'],
                        'soldier_b_id': f['red_soldier_id'],
                        'status': 'PENDING'
                    }
                )
                
                # Evenimentele se numesc 'steps' acum
                if created:
                    total_importate += 1
                    for i, step in enumerate(f.get('steps', [])):
                        FightEvent.objects.create(
                            fight=fight,
                            sequence=i,
                            attacker_id=step['attacker'],
                            defender_id=step['defender'],
                            damage=step['damage']
                        )
    
    # Trecem la următoarea pagină
    current_path = data.get('next')

print(f"\n=========================================")
print(f"GATA! Am importat cu succes {total_importate} lupte noi.")