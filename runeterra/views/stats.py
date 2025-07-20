from django.db.models import Avg, Case, F, IntegerField, Q, When, Min, Max
from django.shortcuts import render

from runeterra.constants.region import Region
from runeterra.models import Champion


def region_stats(request):
    stats = []
    for value, label in Region.choices:
        qs = Champion.objects.filter(Q(primary_region=value) | Q(secondary_region=value))
        total = qs.count()
        unlocked = qs.filter(unlocked=True).count()
        constellation_mean = (
            qs.annotate(
                effective=F("star_level")
                + Case(When(lvl30=True, then=2), default=0, output_field=IntegerField())
            )
            .aggregate(avg=Avg("effective"))
            .get("avg")
            or 0
        )
        level_stats = qs.aggregate(
            mean=Avg("champion_level"),
            min=Min("champion_level"),
            max=Max("champion_level"),
        )
        stats.append(
            {
                "label": label,
                "total": total,
                "unlocked": unlocked,
                "constellation_mean": constellation_mean,
                "level_mean": level_stats.get("mean") or 0,
                "level_min": level_stats.get("min") or 0,
                "level_max": level_stats.get("max") or 0,
            }
        )

    return render(request, "runeterra/region_stats.html", {"stats": stats})
