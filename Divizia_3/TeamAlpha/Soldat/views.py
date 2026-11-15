import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum
from .models import Unit, Fight, FightStep
from .forms import UnitForm

# Task 1: Add a new fighter unit
def add_unit(request):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('all_units')
    else:
        form = UnitForm()
    return render(request, 'add_unit.html', {'form': form})


# Task 2, 3, & 4b: List units, Simulate fight, and Team Statistics
def all_units(request):
    units = Unit.objects.all()

    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_units')
        if len(selected_ids) != 2:
            messages.error(request, "You must select exactly 2 fighters to simulate a fight.")
        else:
            f1 = get_object_or_404(Unit, id=selected_ids[0])
            f2 = get_object_or_404(Unit, id=selected_ids[1])

            if f1.team == f2.team:
                messages.error(request, "Fighters must belong to different teams (Blue vs Red).")
            elif f1.health <= 0 or f2.health <= 0:
                messages.error(request, "Both fighters must have more than 0 health to fight.")
            else:
                # Start Fight Simulation
                fight = Fight.objects.create(fighter1=f1, fighter2=f2)
                attacker, defender = f1, f2

                while f1.health > 0 and f2.health > 0:
                    dmg = random.randint(0, attacker.attack_points)
                    defender.health = max(0, defender.health - dmg)
                    defender.save()

                    FightStep.objects.create(
                        fight=fight,
                        attacker=attacker,
                        defender=defender,
                        damage=dmg,
                        attacker_health_after=attacker.health,
                        defender_health_after=defender.health
                    )

                    # Swap turns
                    attacker, defender = defender, attacker

                fight.winner = f1 if f1.health > 0 else f2
                fight.save()
                messages.success(request, f"Fight complete! Winner: {fight.winner.name}")
                return redirect('all_units')

    # Task 4b: Calculate Team Statistics from Fight History
    stats = {}
    for team in ['Blue', 'Red']:
        fights_count = Fight.objects.filter(Q(fighter1__team=team) | Q(fighter2__team=team)).distinct().count()
        dmg_caused = FightStep.objects.filter(attacker__team=team).aggregate(total=Sum('damage'))['total'] or 0
        dmg_taken = FightStep.objects.filter(defender__team=team).aggregate(total=Sum('damage'))['total'] or 0
        stats[team] = {
            'fights': fights_count,
            'damage_caused': dmg_caused,
            'damage_taken': dmg_taken,
        }

    return render(request, 'all_units.html', {'units': units, 'stats': stats})


# Task 2: Heal action
def heal_unit(request, unit_id):
    if request.method == 'POST':
        unit = get_object_or_404(Unit, id=unit_id)
        unit.health = 100
        unit.save()
    return redirect('all_units')


# Task 2 & 4a: Unit details and fight history cards
def unit_detail(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    fights = Fight.objects.filter(Q(fighter1=unit) | Q(fighter2=unit)).order_by('-created_at')
    return render(request, 'unit_detail.html', {'unit': unit, 'fights': fights})
