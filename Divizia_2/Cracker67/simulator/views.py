import random
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from django.contrib import messages
from .models import Unit, Fight, FightStep
from .forms import UnitForm


def add_unit(request):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('all_units')
    else:
        form = UnitForm()
    return render(request, 'simulator/add_unit.html', {'form': form})


def all_units(request):
    units = Unit.objects.all()
    stats = {}
    for team in ['Blue', 'Red']:
        team_fights = Fight.objects.filter(Q(fighter1__team=team) | Q(fighter2__team=team)).distinct().count()
        damage_caused = FightStep.objects.filter(attacker__team=team).aggregate(total=Sum('damage'))['total'] or 0
        damage_taken = FightStep.objects.filter(defender__team=team).aggregate(total=Sum('damage'))['total'] or 0
        stats[team] = {
            'fights': team_fights,
            'damage_caused': damage_caused,
            'damage_taken': damage_taken,
        }
    return render(request, 'simulator/all_units.html', {'units': units, 'stats': stats})


def heal_unit(request, unit_id):
    if request.method == 'POST':
        unit = get_object_or_404(Unit, id=unit_id)
        unit.health = 100
        unit.save()
    return redirect('all_units')


def simulate_fight(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_units')
        if len(selected_ids) != 2:
            messages.error(request, "Selectează exact 2 luptători!")
            return redirect('all_units')
        f1 = get_object_or_404(Unit, id=selected_ids[0])
        f2 = get_object_or_404(Unit, id=selected_ids[1])
        if f1.team == f2.team:
            messages.error(request, "Luptătorii trebuie să fie din echipe diferite!")
            return redirect('all_units')
        if f1.health <= 0 or f2.health <= 0:
            messages.error(request, "Ambii luptători trebuie să aibă viață > 0!")
            return redirect('all_units')

        fight = Fight.objects.create(fighter1=f1, fighter2=f2)
        attacker, defender = f1, f2
        while f1.health > 0 and f2.health > 0:
            dmg = random.randint(0, attacker.attack_points)
            defender.health = max(0, defender.health - dmg)
            defender.save()
            FightStep.objects.create(
                fight=fight, attacker=attacker, defender=defender,
                damage=dmg, attacker_health_after=attacker.health,
                defender_health_after=defender.health
            )
            attacker, defender = defender, attacker
        fight.winner = f1 if f1.health > 0 else f2
        fight.save()
    return redirect('all_units')


def unit_detail(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    fights = Fight.objects.filter(Q(fighter1=unit) | Q(fighter2=unit)).order_by('-created_at')
    return render(request, 'simulator/unit_detail.html', {'unit': unit, 'fights': fights})

def delete_unit(request, unit_id):
    if request.method == 'POST':
        unit = get_object_or_404(Unit, id=unit_id)
        unit.delete()
    return redirect('all_units')

from django.shortcuts import render

# Create your views here.
