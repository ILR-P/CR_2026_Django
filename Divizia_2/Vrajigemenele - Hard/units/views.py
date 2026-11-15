from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from . import services
from .forms import FightForm, UnitForm
from .models import Fight, Unit


@require_http_methods(["GET", "POST"])
def unit_create(request):
    if request.method == "POST":
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f"{unit.name} joined the {unit.get_team_display()} army.")
            return redirect("unit-all")
    else:
        form = UnitForm()
    return render(request, "units/unit_form.html", {"form": form})


@require_http_methods(["GET", "POST"])
def unit_list(request):
    fight_form = FightForm()
    if request.method == "POST":
        fight_form = FightForm(request.POST)
        if fight_form.is_valid():
            a, b = fight_form.cleaned_data["units"]
            fight = services.run_fight(a.pk, b.pk)
            messages.success(request, f"Fight #{fight.pk}: {fight.winner.name} defeated "
                                      f"{(fight.unit_b if fight.winner_id == fight.unit_a_id else fight.unit_a).name} "
                                      f"in {fight.steps.count()} hits.")
            return redirect("unit-all")
    return render(request, "units/unit_list.html", {
        "units": Unit.objects.all(), "fight_form": fight_form, "stats": services.team_stats(),
    })


@require_POST
def unit_heal(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    services.heal(unit.pk)
    messages.success(request, f"{unit.name} was fully healed.")
    return redirect(request.POST.get("next") or "unit-all")


def unit_detail(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    fights = (
        Fight.objects.filter(Q(unit_a=unit) | Q(unit_b=unit))
        .select_related("unit_a", "unit_b", "winner")
        .prefetch_related("steps__attacker", "steps__defender")
    )
    return render(request, "units/unit_detail.html", {"unit": unit, "fights": fights})
