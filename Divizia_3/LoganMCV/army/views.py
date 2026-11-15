from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import UnitForm
from .models import MAX_HEALTH, Fight, Unit
from .services import simulate_fight, team_stats, validate_pair


def _fights_qs():
    return Fight.objects.select_related("unit_a", "unit_b", "winner").prefetch_related(
        "steps__attacker", "steps__defender"
    )


def unit_create(request):
    form = UnitForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Unit added.")
        return redirect("unit_list")
    return render(request, "army/unit_form.html", {"form": form})


def unit_list(request):
    return render(request, "army/unit_list.html", {
        "units": Unit.objects.all(),
        "stats": team_stats(),
        "max_health": MAX_HEALTH,
    })


def unit_detail(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    fights = _fights_qs().filter(Q(unit_a=unit) | Q(unit_b=unit))
    return render(request, "army/unit_detail.html", {
        "unit": unit, "fights": fights, "max_health": MAX_HEALTH,
    })


@require_POST
def unit_heal(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    unit.health = MAX_HEALTH
    unit.save(update_fields=["health"])
    nxt = request.POST.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect("unit_list")


@require_POST
def simulate(request):
    ids = request.POST.getlist("units")
    found = {str(u.pk): u for u in Unit.objects.filter(pk__in=ids)}
    units = [found[i] for i in ids if i in found]   # keep the order of the list
    error = validate_pair(units)
    if error:
        messages.error(request, error)
        return redirect("unit_list")
    fight = simulate_fight(*units)
    return redirect("fight_detail", pk=fight.pk)


def fight_detail(request, pk):
    fight = get_object_or_404(_fights_qs(), pk=pk)
    return render(request, "army/fight_detail.html", {"fight": fight})
