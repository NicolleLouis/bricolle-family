from django.db.models import Q
from django.shortcuts import render

from runeterra.constants.region import Region
from runeterra.models import Champion


def random_picker(request):
    champion = None
    only_unlocked = False
    only_lvl30 = False
    selected_region = ""
    min_star_level = 0
    min_level = 0
    max_level = 60

    if request.method == "POST":
        only_unlocked = bool(request.POST.get("only_unlocked"))
        only_lvl30 = bool(request.POST.get("only_lvl30"))
        selected_region = request.POST.get("region", "")
        try:
            min_star_level = int(request.POST.get("min_star_level", 0))
        except (TypeError, ValueError):
            min_star_level = 0
        try:
            min_level = int(request.POST.get("min_level", 0))
        except (TypeError, ValueError):
            min_level = 0
        try:
            max_level = int(request.POST.get("max_level", 60))
        except (TypeError, ValueError):
            max_level = 60

        queryset = Champion.objects.all()

        if only_unlocked:
            queryset = queryset.filter(unlocked=True)
        if only_lvl30:
            queryset = queryset.filter(lvl30=True)
        if selected_region:
            queryset = queryset.filter(
                Q(primary_region=selected_region) | Q(secondary_region=selected_region)
            )
        if min_star_level:
            queryset = queryset.filter(star_level__gte=min_star_level)
        if min_level:
            queryset = queryset.filter(champion_level__gte=min_level)
        if max_level:
            queryset = queryset.filter(champion_level__lte=max_level)

        champion = queryset.order_by("?").first()

    return render(
        request,
        "runeterra/random_picker.html",
        {
            "champion": champion,
            "only_unlocked": only_unlocked,
            "only_lvl30": only_lvl30,
            "selected_region": selected_region,
            "min_star_level": min_star_level,
            "min_level": min_level,
            "max_level": max_level,
            "regions": Region,
        },
    )
