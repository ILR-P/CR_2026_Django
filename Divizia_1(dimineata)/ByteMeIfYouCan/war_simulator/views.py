import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Unit, Fight, FightStep
from .forms import UnitForm


def get_team_stats():
    stats = {}
    for team in ['Blue', 'Red']:
        fight_count = Fight.objects.filter(
            Q(fighter_1__team=team) | Q(fighter_2__team=team)
        ).distinct().count()

        damage_caused = FightStep.objects.filter(
            attacker__team=team
        ).aggregate(total=Sum('damage'))['total'] or 0

        damage_taken = FightStep.objects.filter(
            defender__team=team
        ).aggregate(total=Sum('damage'))['total'] or 0

        stats[team] = {
            'fights': fight_count,
            'damage_caused': damage_caused,
            'damage_taken': damage_taken,
        }
    return stats


def unit_create(request):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fighter added successfully!")
            return redirect('unit_all')
    else:
        form = UnitForm()

    return render(request, 'war_simulator/unit_form.html', {'form': form})


def unit_all(request):
    error_message = None

    if request.method == 'POST':
        # Check if heal requested on unit_all
        action = request.POST.get('action')
        heal_id = request.POST.get('heal_unit_id') or request.POST.get('unit_id')
        if action == 'heal' or (heal_id and 'simulate' not in request.POST):
            unit = get_object_or_404(Unit, pk=heal_id)
            unit.health = 100
            unit.save()
            messages.success(request, f"{unit.name} has been restored to 100 HP.")
            return redirect('unit_all')

        # Otherwise it's a simulate fight request
        fighter_ids = []
        if request.content_type == 'application/json':
            try:
                payload = json.loads(request.body)
                if isinstance(payload, dict):
                    fighter_ids = payload.get('fighter_ids') or [payload.get('fighter_1'), payload.get('fighter_2')]
                elif isinstance(payload, list):
                    fighter_ids = payload
            except Exception:
                fighter_ids = []
        else:
            fighter_ids = (
                request.POST.getlist('fighter_ids')
                or request.POST.getlist('fighter_ids[]')
            )
            if not fighter_ids:
                f1 = request.POST.get('fighter_1') or request.POST.get('fighter1')
                f2 = request.POST.get('fighter_2') or request.POST.get('fighter2')
                if f1 or f2:
                    fighter_ids = [fid for fid in [f1, f2] if fid]

        if not isinstance(fighter_ids, (list, tuple)) or len(fighter_ids) != 2:
            error_message = "Please select exactly 2 fighters to simulate a fight."
        else:
            try:
                fighter_1 = Unit.objects.get(pk=fighter_ids[0])
                fighter_2 = Unit.objects.get(pk=fighter_ids[1])

                if fighter_1.id == fighter_2.id:
                    error_message = "Fighters must be distinct."
                elif fighter_1.health <= 0 or fighter_2.health <= 0:
                    error_message = "Both fighters must have health greater than 0."
                elif fighter_1.team == fighter_2.team:
                    error_message = "Fighters must belong to different teams (Blue vs Red)."
                else:
                    # Execute fight simulation
                    fight = Fight.objects.create(fighter_1=fighter_1, fighter_2=fighter_2)
                    step_number = 1
                    steps = []

                    # Combat loop: While both fighters have health > 0
                    while (
                        fighter_1.health > 0
                        and fighter_2.health > 0
                        and (fighter_1.attack_points > 0 or fighter_2.attack_points > 0)
                    ):
                        # fighter_1 attacks fighter_2
                        damage_1 = random.randint(0, fighter_1.attack_points)
                        fighter_2.health = max(0, fighter_2.health - damage_1)
                        steps.append(FightStep(
                            fight=fight,
                            step_number=step_number,
                            attacker=fighter_1,
                            defender=fighter_2,
                            damage=damage_1,
                            attacker_health_after=fighter_1.health,
                            defender_health_after=fighter_2.health
                        ))
                        step_number += 1

                        # if fighter_2.health > 0, fighter_2 attacks fighter_1
                        if fighter_2.health > 0:
                            damage_2 = random.randint(0, fighter_2.attack_points)
                            fighter_1.health = max(0, fighter_1.health - damage_2)
                            steps.append(FightStep(
                                fight=fight,
                                step_number=step_number,
                                attacker=fighter_2,
                                defender=fighter_1,
                                damage=damage_2,
                                attacker_health_after=fighter_2.health,
                                defender_health_after=fighter_1.health
                            ))
                            step_number += 1

                        if step_number > 1000:
                            # Stalemate safety
                            break

                    FightStep.objects.bulk_create(steps)
                    fighter_1.save()
                    fighter_2.save()

                    if fighter_1.health > 0 and fighter_2.health == 0:
                        fight.winner = fighter_1
                    elif fighter_2.health > 0 and fighter_1.health == 0:
                        fight.winner = fighter_2
                    else:
                        fight.winner = None
                    fight.save()

                    messages.success(
                        request,
                        f"Fight completed! Winner: {fight.winner.name if fight.winner else 'Draw'}."
                    )
                    return redirect('unit_all')
            except (Unit.DoesNotExist, TypeError, ValueError):
                error_message = "One or both selected fighters do not exist."

        if error_message:
            messages.error(request, error_message)

    units = Unit.objects.all().order_by('id')
    team_stats = get_team_stats()

    return render(request, 'war_simulator/unit_all.html', {
        'units': units,
        'team_stats': team_stats,
        'error_message': error_message,
    })


@require_POST
def unit_heal(request, unit_id):
    unit = get_object_or_404(Unit, pk=unit_id)
    unit.health = 100
    unit.save()
    messages.success(request, f"{unit.name} has been restored to 100 HP.")
    next_url = request.POST.get('next', '')
    if url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect('unit_all')


@require_POST
def clear_game_data(request):
    with transaction.atomic():
        Fight.objects.all().delete()
        Unit.objects.all().delete()
    messages.success(request, 'Fighters and fight history have been cleared.')
    return redirect('unit_all')


@require_GET
def unit_detail(request, unit_id):
    unit = get_object_or_404(Unit, pk=unit_id)
    fights = Fight.objects.filter(
        Q(fighter_1=unit) | Q(fighter_2=unit)
    ).order_by('-created_at').prefetch_related('steps__attacker', 'steps__defender')

    return render(request, 'war_simulator/unit_detail.html', {
        'unit': unit,
        'fights': fights,
    })
