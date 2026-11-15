from django.shortcuts import render

from .models import Fight
from .tasks import simulate_fight


def simulate(request):
    # Marchează atomic ca QUEUED ca un refresh să nu pună aceeași luptă de două ori.
    for fight_id in list(Fight.objects.filter(status=Fight.PENDING).values_list("pk", flat=True)):
        if Fight.objects.filter(pk=fight_id, status=Fight.PENDING).update(status=Fight.QUEUED):
            simulate_fight.delay(fight_id)

    fights = (Fight.objects.select_related("soldier_a", "soldier_b", "winner")
              .prefetch_related("events__attacker", "events__defender").order_by("pk"))
    running = any(f.status in (Fight.QUEUED, Fight.RUNNING) for f in fights)
    return render(request, "army/simulate.html", {"fights": fights, "running": running})