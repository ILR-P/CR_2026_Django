from django.http import HttpResponseBadRequest
from django.db.models import Count
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from . import services
from .forms import SimulationActionForm
from .models import Fight, Soldier
from .tasks import download_fight_batch, simulate_fight


def _launch_pending():
    """One independent background task per PENDING fight.
    claim_fight() inside simulate_fight makes a double-launch harmless."""
    ids = list(Fight.objects.filter(status=Fight.PENDING).values_list("id", flat=True))
    for fid in ids:
        simulate_fight.delay(fid)
    return len(ids)


@require_http_methods(["GET", "HEAD", "POST"])
def simulate(request):
    if request.method == "POST":
        form = SimulationActionForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data["action"]
            if action == SimulationActionForm.RESET:
                services.reset_all()
            elif action == SimulationActionForm.LOAD_FIGHTS:
                host = form.cleaned_data.get("host", "").strip()
                if host:
                    download_fight_batch.delay(host, 0)
                else:
                    return HttpResponseBadRequest("host is required for load-fights action")
            return redirect("simulate")  # Post/Redirect/Get: a refresh won't resubmit
        return HttpResponseBadRequest("Invalid action")

    _launch_pending()  # visiting the page replays every fight that hasn't run yet

    fights = (
        Fight.objects.select_related("soldier_a__person", "soldier_b__person")
        .prefetch_related("events__attacker__person", "events__defender__person")
        .order_by("id")
    )
    soldiers = Soldier.objects.select_related("person").order_by("-health", "person_id")
    counts = {s: n for s, n in Fight.objects.values_list("status").annotate(n=Count("id"))}
    running = counts.get(Fight.PENDING, 0) + counts.get(Fight.RUNNING, 0)
    return render(request, "battle/simulate.html", {
        "form": SimulationActionForm(),
        "fights": fights, "soldiers": soldiers, "counts": counts,
        "total": sum(counts.values()), "unfinished": running,
    })
