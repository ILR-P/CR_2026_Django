from django.shortcuts import render, redirect, get_object_or_404
from .forms import UnitForm
from .models import Unit, Fight, FightHistory
import random

def add_unit(request):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/unit/all')  # Redirects to your list page for Task 2
    else:
        form = UnitForm()

    return render(request, 'add-unit-form.html', {'form': form})

from django.db.models import Q, Sum, Count


def unit_list(request):
    units = Unit.objects.all()

    teams = ['Blue', 'Red']
    team_stats = {}

    for team in teams:
        team_units = Unit.objects.filter(team=team)

        fights_count = Fight.objects.filter(
            Q(fighter1__team=team) | Q(fighter2__team=team)
        ).count()

        # Overall damage caused (sum of damage_dealt where attacker is in team)
        damage_caused = FightHistory.objects.filter(
            attacker__team=team
        ).aggregate(total=Sum('damage_dealt'))['total'] or 0

        # Overall damage taken (sum of damage_dealt where defender is in team)
        damage_taken = FightHistory.objects.filter(
            defender__team=team
        ).aggregate(total=Sum('damage_dealt'))['total'] or 0

        team_stats[team] = {
            'fights_count': fights_count,
            'damage_caused': damage_caused,
            'damage_taken': damage_taken,
        }

    return render(request, 'unit_list.html', {
        'units': units,
        'team_stats': team_stats
    })


def unit_detail(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    # Task 4a: Get all fights this unit participated in
    fights = Fight.objects.filter(Q(fighter1=unit) | Q(fighter2=unit)).order_by('-created_at')

    return render(request, 'unit_detail.html', {
        'unit': unit,
        'fights': fights
    })

def heal_unit(request, unit_id):
    if request.method == 'POST':
        unit = get_object_or_404(Unit, id=unit_id)
        unit.health = 100  # Restores health to maximum (assuming max health is 100)
        unit.save()
    return redirect('/unit/all')

def simulate_fight_view(request):
    units = Unit.objects.all()
    error = None

    if request.method == 'POST':
        f1_id = request.POST.get('fighter1')
        f2_id = request.POST.get('fighter2')

        if f1_id == f2_id:
            error = "A fighter cannot battle themselves!"
        else:
            f1 = get_object_or_404(Unit, id=f1_id)
            f2 = get_object_or_404(Unit, id=f2_id)

            if f1.team == f2.team:
                error = "Fighters must be of different teams (Blue vs Red)!"
            else:
                # Create Fight instance
                fight = Fight.objects.create(fighter1=f1, fighter2=f2)

                # Simulation loop variables
                hp1 = f1.health
                hp2 = f2.health

                # Determine starting turn order (e.g. alternating)
                current_attacker, current_defender = f1, f2
                hp_attacker, hp_defender = hp1, hp2

                step = 1
                winner = None

                while hp_attacker > 0 and hp_defender > 0:
                    # Random damage between 0 and attacker's attack points
                    damage = random.randint(0, current_attacker.attack_points)
                    hp_defender = max(0, hp_defender - damage)

                    # Map healths back to f1 and f2 for logging
                    if current_attacker == f1:
                        hp1, hp2 = hp_attacker, hp_defender
                    else:
                        hp2, hp1 = hp_attacker, hp_defender

                    # Record step history
                    FightHistory.objects.create(
                        fight=fight,
                        step_number=step,
                        attacker=current_attacker,
                        defender=current_defender,
                        damage_dealt=damage,
                        attacker_health_after=hp_attacker,
                        defender_health_after=hp_defender
                    )

                    if hp_defender <= 0:
                        winner = current_attacker
                        break

                    # Swap attacker and defender for next turn
                    current_attacker, current_defender = current_defender, current_attacker
                    hp_attacker, hp_defender = hp_defender, hp_attacker
                    step += 1

                # Save winner and update final health in DB
                fight.winner = winner
                fight.save()

                f1.health = max(0, hp1)
                f2.health = max(0, hp2)
                f1.save()
                f2.save()

                return redirect(f'/fight/result/{fight.id}')

    return render(request, 'simulate_fight.html', {'units': units, 'error': error})


def fight_result_view(request, fight_id):
    fight = get_object_or_404(Fight, id=fight_id)
    steps = fight.history_steps.all()
    return render(request, 'fight_result.html', {'fight': fight, 'steps': steps})



