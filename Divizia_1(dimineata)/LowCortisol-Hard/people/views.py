from django.http import JsonResponse

from .models import Person


def draft_status(request):
    people = Person.objects.order_by("id").values("id", "name", "age", "rank")
    drafted = sum(1 for person in people if person["rank"] is not None)
    return JsonResponse({"total": len(people), "drafted": drafted, "people": list(people)})
