import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import FighterUnit, FightHistory
from .forms import FighterUnitForm


def add_unit(request):
    if request.method == 'POST':
        form = FighterUnitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fighter unit added successfully!')
            return redirect('list_units')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FighterUnitForm(initial={'health': 100})

    return render(request, 'unit/add_unit.html', {'form': form})


def list_units(request):
    if request.method == 'POST':
        if 'heal' in request.POST:
            unit_id = request.POST.get('unit_id')
            unit = get_object_or_404(FighterUnit, id=unit_id)
            unit.health = 100
            unit.save()
            messages.success(request, f'{unit.name} has been fully healed!')

        elif 'simulate' in request.POST:
            unit1_id = request.POST.get('unit1_id')
            unit2_id = request.POST.get('unit2_id')

            if unit1_id and unit2_id:
                u1 = get_object_or_404(FighterUnit, id=unit1_id)
                u2 = get_object_or_404(FighterUnit, id=unit2_id)

                if u1.team != u2.team and u1.health > 0 and u2.health > 0:
                    simulate_fight(u1, u2)
                    messages.success(request, 'Fight simulation completed!')
                else:
                    messages.error(request, 'Select two alive units from DIFFERENT teams.')

        return redirect('list_units')

    units = FighterUnit.objects.all()

    stats = {
        'Blue': {'fights': 0, 'damage_taken': 0, 'damage_caused': 0},
        'Red': {'fights': 0, 'damage_taken': 0, 'damage_caused': 0}
    }

    for fight in FightHistory.objects.all():
        stats[fight.attacker.team]['fights'] += 1
        stats[fight.defender.team]['fights'] += 1

        for step in fight.fight_log:
            dmg = step['damage']
            stats[step['attacker_team']]['damage_caused'] += dmg
            stats[step['defender_team']]['damage_taken'] += dmg

    context = {'units': units, 'stats': stats}
    return render(request, 'unit/list_units.html', context)


def simulate_fight(u1, u2):
    fighters = [u1, u2]
    random.shuffle(fighters)
    attacker, defender = fighters[0], fighters[1]

    fight_log = []

    while attacker.health > 0 and defender.health > 0:
        damage = attacker.attack_points
        defender.health = max(0, defender.health - damage)

        fight_log.append({
            'attacker_name': attacker.name,
            'attacker_team': attacker.team,
            'defender_name': defender.name,
            'defender_team': defender.team,
            'damage': damage,
            'attacker_health': attacker.health,
            'defender_health': defender.health
        })

        if defender.health > 0:
            attacker, defender = defender, attacker

    winner = attacker if attacker.health > 0 else defender

    u1.save()
    u2.save()

    FightHistory.objects.create(
        attacker=u1,
        defender=u2,
        winner=winner,
        fight_log=fight_log
    )


def unit_detail(request, unit_id):
    unit = get_object_or_404(FighterUnit, id=unit_id)
    fights_as_attacker = unit.fights_as_attacker.all()
    fights_as_defender = unit.fights_as_defender.all()
    all_fights = (fights_as_attacker | fights_as_defender).order_by('-created_at')

    return render(request, 'unit/unit_detail.html', {'unit': unit, 'fights': all_fights})