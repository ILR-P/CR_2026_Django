from django.conf import settings
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import tasks
from .models import Fight, FightEvent, Person


def counters():
    return {
        'registered': Person.objects.count(),
        'drafted': Person.objects.exclude(rank='').count(),
        'n_fights': Fight.objects.count(),
        'n_events': FightEvent.objects.count(),
        'n_simulated': Fight.objects.filter(simulated=True).count(),
        'max_health': settings.MAX_HEALTH,
    }


def index(request):
    context = counters()
    context['people'] = Person.objects.all()
    return render(request, 'war/index.html', context)


@require_POST
def start(request):
    tasks.register_people.delay()
    return redirect('war:index')


def fights(request):
    context = counters()
    context['fights'] = Fight.objects.select_related('blue', 'red', 'winner').annotate(
        n_events=Count('events'), damage=Sum('events__damage')
    )
    return render(request, 'war/fights.html', context)


def fight_detail(request, external_id):
    fight = get_object_or_404(
        Fight.objects.select_related('blue', 'red', 'winner'), external_id=external_id
    )
    context = counters()
    context['fight'] = fight
    context['events'] = fight.events.select_related('attacker', 'defender')
    return render(request, 'war/fight_detail.html', context)


def simulate(request):
    context = counters()
    context['fights'] = Fight.objects.select_related('blue', 'red', 'winner').annotate(
        n_events=Count('events'), damage=Sum('events__damage')
    )
    context['fallen'] = Person.objects.filter(health=0).count()
    context['damage'] = FightEvent.objects.aggregate(d=Sum('damage'))['d'] or 0
    return render(request, 'war/simulate.html', context)


@require_POST
def simulate_run(request):
    tasks.simulate_all.delay()
    return redirect('war:simulate')


@require_POST
def simulate_reset(request):
    tasks.reset.delay()
    return redirect('war:simulate')
