from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import UnitForm
from .models import MAX_HEALTH, Unit
from .services import FightError, simulate_fight, team_statistics


def unit_add(request):
    if request.method == "POST":
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            messages.success(request, f"{unit.name} was added to the army.")
            return redirect("unit-all")
    else:
        form = UnitForm(initial={"health": MAX_HEALTH, "attack_points": 10})
    return render(request, "war/unit_form.html", {"form": form})


def unit_all(request):
    return render(request, "war/unit_list.html", {
        "units": Unit.objects.all(),
        "stats": team_statistics(),
    })


def unit_detail(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    return render(request, "war/unit_detail.html", {"unit": unit, "fights": unit.fights()})


@require_POST
def unit_heal(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    unit.health = MAX_HEALTH
    unit.save(update_fields=["health"])
    messages.success(request, f"{unit.name} was healed.")
    target = request.POST.get("next", "")
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return redirect(target)
    return redirect("unit-all")


@require_POST
def unit_simulate(request):
    ids = request.POST.getlist("fighters")
    units = list(Unit.objects.filter(pk__in=[i for i in ids if i.isdigit()]))
    if len(set(ids)) != 2 or len(units) != 2:
        messages.error(request, "Select exactly two fighters.")
        return redirect("unit-all")
    by_id = {str(u.pk): u for u in units}
    try:
        simulate_fight(by_id[ids[0]], by_id[ids[1]])
    except FightError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "The fight is over. See the fighters' pages for the full history.")
    return redirect("unit-all")
