
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction
from random import randint

from .models import Unit, Fight, FightTurn
from .forms import UnitForm
def add_unit(request):

    if request.method == "POST":

        form = UnitForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Fighter successfully added!"
            )

            return redirect("all_units")

        else:
            messages.error(
                request,
                "Please correct the errors in the form."
            )

    else:
        form = UnitForm()

    return render(
        request,
        "units/add_unit.html",
        {"form": form}
    )
def all_units(request):

    units = Unit.objects.all().order_by("id")

    return render(
        request,
        "units/all_units.html",
        {"units": units}
    )
def unit_details(request, unit_id):

    unit = get_object_or_404(
        Unit,
        id=unit_id
    )

    fights = Fight.objects.filter(
        models_Q_unit(unit)
    ).select_related(
        "unit1", "unit2", "winner"
    ).prefetch_related(
        "turns__attacker",
        "turns__defender"
    ).order_by("-created_at")

    return render(
        request,
        "units/unit_details.html",
        {
            "unit": unit,
            "fights": fights
        }
    )
@require_POST
def heal_unit(request, unit_id):

    with transaction.atomic():

        unit = get_object_or_404(
            Unit.objects.select_for_update(),
            id=unit_id
        )

        unit.health = 100
        unit.save(update_fields=["health"])

    messages.success(
        request,
        f"{unit.name} has been healed!"
    )

    return redirect("all_units")
@require_POST
def simulate_fight(request):

    try:
        unit1_id = int(request.POST.get("unit1_id"))
        unit2_id = int(request.POST.get("unit2_id"))

    except (TypeError, ValueError):
        messages.error(
            request,
            "Please select two valid fighters."
        )
        return redirect("all_units")

    if unit1_id == unit2_id:
        messages.error(
            request,
            "You must select two different fighters."
        )
        return redirect("all_units")

    try:

        with transaction.atomic():

            # Retrieve and lock both fighters
            units = {
                unit.id: unit
                for unit in Unit.objects.select_for_update()
                .filter(id__in=[unit1_id, unit2_id])
                .order_by("id")
            }

            if len(units) != 2:
                raise ValueError(
                    "One or both fighters do not exist."
                )

            unit1 = units[unit1_id]
            unit2 = units[unit2_id]

            # Validate teams
            if unit1.team == unit2.team:
                raise ValueError(
                    "Fighters must belong to different teams."
                )

            # Validate health
            if unit1.health <= 0 or unit2.health <= 0:
                raise ValueError(
                    "Both fighters must have health above zero."
                )

            # Create fight record
            fight = Fight.objects.create(
                unit1=unit1,
                unit2=unit2
            )

            attacker = unit1
            defender = unit2

            turn_number = 1

            # Safety limit
            max_turns = 10000

            # Fight simulation
            while (
                unit1.health > 0
                and unit2.health > 0
                and turn_number <= max_turns
            ):

                damage = randint(
                    0,
                    attacker.attack_points
                )

                defender.health = max(
                    0,
                    defender.health - damage
                )

                defender.save(
                    update_fields=["health"]
                )

                FightTurn.objects.create(
                    fight=fight,
                    attacker=attacker,
                    defender=defender,
                    attack_points=damage,
                    attacker_health=attacker.health,
                    defender_health=defender.health,
                    turn_number=turn_number
                )

                turn_number += 1

                attacker, defender = defender, attacker

            if unit1.health == 0 and unit2.health == 0:
                fight.winner = None

            elif unit1.health == 0:
                fight.winner = unit2

            elif unit2.health == 0:
                fight.winner = unit1

            else:
                fight.winner = None

            fight.save(update_fields=["winner"])

        messages.success(
            request,
            "Fight completed successfully!"
        )

    except ValueError as error:

        messages.error(request, str(error))

        return redirect("all_units")

    except Exception:

        messages.error(
            request,
            "An error occurred while saving the fight."
        )

        return redirect("all_units")

    return redirect(
        "unit_details",
        unit_id=unit1_id
    )

def models_Q_unit(unit):

    from django.db.models import Q

    return Q(unit1=unit) | Q(unit2=unit)

