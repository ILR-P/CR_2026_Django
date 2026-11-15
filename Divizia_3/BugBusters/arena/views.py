import random

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import FighterForm
from .models import Fight, Fighter, Step


def unit_add(request):
    form = FighterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        unit = form.save(commit=False)
        unit.max_health = unit.health
        unit.save()
        return redirect('unit_list')
    return render(request, 'unit_form.html', {'form': form})


def unit_list(request):
    error = ''
    if request.method == 'POST':
        chosen = list(Fighter.objects.filter(id__in=request.POST.getlist('fighters')))
        if len(chosen) != 2:
            error = 'Select exactly two fighters.'
        elif chosen[0].team == chosen[1].team:
            error = 'Fighters must be from different teams.'
        else:
            fight = simulate(*chosen)
            return redirect('unit_detail', fight.winner_id)

    stats = {team: {'fights': 0, 'caused': 0, 'taken': 0} for team in ('A', 'B')}
    for step in Step.objects.select_related('attacker', 'defender'):
        stats[step.attacker.team]['caused'] += step.damage
        stats[step.defender.team]['taken'] += step.damage
    for fight in Fight.objects.select_related('first', 'second'):
        stats[fight.first.team]['fights'] += 1
        stats[fight.second.team]['fights'] += 1

    return render(request, 'unit_list.html',
                  {'units': Fighter.objects.all(), 'error': error, 'stats': stats})


def unit_detail(request, pk):
    unit = get_object_or_404(Fighter, pk=pk)
    fights = (Fight.objects.filter(Q(first=unit) | Q(second=unit))
              .prefetch_related('steps__attacker', 'steps__defender'))
    return render(request, 'unit_detail.html', {'unit': unit, 'fights': fights})


@require_POST
def unit_heal(request, pk):
    unit = get_object_or_404(Fighter, pk=pk)
    unit.health = unit.max_health
    unit.save()
    return redirect('unit_list')


def simulate(a, b):
    fight = Fight.objects.create(first=a, second=b)
    attacker, defender = a, b
    while a.health > 0 and b.health > 0:
        damage = random.randint(0, attacker.attack_points)
        defender.health = max(0, defender.health - damage)
        Step.objects.create(fight=fight, attacker=attacker, defender=defender, damage=damage,
                            attacker_health=attacker.health, defender_health=defender.health)
        attacker, defender = defender, attacker
    fight.winner = a if a.health > 0 else b
    fight.save()
    a.save()
    b.save()
    return fight
    
