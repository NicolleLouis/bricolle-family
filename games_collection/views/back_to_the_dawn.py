from django.db.models import Case, IntegerField, When
from django.shortcuts import render

from games_collection.models import BttdAnimal, BttdObject, BttdDesire, DesireStatus


PREFERENCE_ORDER = Case(
    When(status=DesireStatus.LOVE, then=0),
    When(status=DesireStatus.LIKE, then=1),
    When(status=DesireStatus.NEUTRAL, then=2),
    When(status=DesireStatus.DISLIKE, then=3),
    output_field=IntegerField(),
)


def back_to_the_dawn(request):
    animal_query = request.GET.get("animal")
    object_query = request.GET.get("object")

    animal_results = (
        BttdDesire.objects.select_related("object")
        .filter(animal__name__icontains=animal_query)
        .order_by(PREFERENCE_ORDER)
        if animal_query
        else None
    )

    object_results = (
        BttdDesire.objects.select_related("animal")
        .filter(object__name__icontains=object_query)
        .order_by(PREFERENCE_ORDER)
        if object_query
        else None
    )

    context = {
        "animal_results": animal_results,
        "object_results": object_results,
        "animal_query": animal_query or "",
        "object_query": object_query or "",
    }
    return render(request, "games_collection/back_to_the_dawn.html", context)
