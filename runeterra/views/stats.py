from django.db.models import Avg, Case, F, IntegerField, Q, When
from django.shortcuts import render

from runeterra.constants.region import Region
from runeterra.models import Champion


def region_stats(request):
    stats = []
    for value, label in Region.choices:
        qs = Champion.objects.filter(Q(primary_region=value) | Q(secondary_region=value))
        total = qs.count()
        unlocked = qs.filter(unlocked=True).count()
        avg = (
            qs.annotate(
                effective=F("star_level")
                + Case(When(lvl30=True, then=2), default=0, output_field=IntegerField())
            )
            .aggregate(avg=Avg("effective"))
            .get("avg")
            or 0
        )
        stats.append({"label": label, "total": total, "unlocked": unlocked, "avg": avg})

    return render(request, "runeterra/region_stats.html", {"stats": stats})
