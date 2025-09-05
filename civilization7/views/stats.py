from django.db.models import Count
from django.shortcuts import render

from civilization7.constants.victoire import Victoire
from civilization7.models import Game


def stats(request):
    total_games = Game.objects.count()
    victories = Game.objects.filter(victory=True).count()
    victories_raw = (
        Game.objects.filter(victory=True)
        .values("victory_type")
        .annotate(count=Count("id"))
    )
    victory_choices = list(Victoire.choices)
    victory_map = {value: 0 for value, _ in victory_choices}
    for item in victories_raw:
        victory_map[item["victory_type"]] = item["count"]
    victories_by_type = [
        (label, victory_map[value]) for value, label in victory_choices
    ]
    return render(
        request,
        "civilization7/stats.html",
        {
            "total_games": total_games,
            "victories": victories,
            "victories_by_type": victories_by_type,
        },
    )
