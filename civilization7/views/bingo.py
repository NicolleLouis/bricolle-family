from django.db.models import Q
from django.shortcuts import render

from civilization7.constants.victory import Victory
from civilization7.models import Civilization, Game, Leader


def bingo_leader(request):
    victory_choices = list(Victory.choices)
    rows = []
    for leader in Leader.objects.all().order_by("name"):
        results = [
            Game.objects.filter(
                leader=leader, victory=True, victory_type=value
            ).exists()
            for value, _ in victory_choices
        ]
        rows.append({"leader": leader, "results": results})
    return render(
        request,
        "civilization7/bingo_leader.html",
        {"victory_choices": victory_choices, "rows": rows},
    )


def bingo_civilization(request):
    victory_choices = list(Victory.choices)
    rows = []
    civs = Civilization.objects.all().order_by("name")
    for civ in civs:
        results = [
            Game.objects.filter(
                victory=True,
                victory_type=value,
            ).filter(
                Q(ancient_civ=civ)
                | Q(exploration_civ=civ)
                | Q(modern_civ=civ)
            ).exists()
            for value, _ in victory_choices
        ]
        rows.append({"civilization": civ, "results": results})
    return render(
        request,
        "civilization7/bingo_civilization.html",
        {"victory_choices": victory_choices, "rows": rows},
    )
