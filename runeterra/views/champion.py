from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from runeterra.constants.region import Region
from runeterra.forms.champion import ChampionForm
from runeterra.models import Champion


def champion_list(request):
    champions = Champion.objects.all()

    region = request.GET.get("region", "")
    star_level = request.GET.get("star_level")
    only_unlocked = request.GET.get("only_unlocked") is not None
    only_lvl30 = request.GET.get("only_lvl30") is not None
    sort = request.GET.get("sort", "name")

    if region:
        champions = champions.filter(
            Q(primary_region=region) | Q(secondary_region=region)
        )
    if star_level:
        try:
            star_level_value = int(star_level)
            champions = champions.filter(star_level__gte=star_level_value)
        except (TypeError, ValueError):
            pass
    if only_unlocked:
        champions = champions.filter(unlocked=True)
    if only_lvl30:
        champions = champions.filter(lvl30=True)

    if sort == "star_level":
        champions = champions.order_by("-star_level", "name")
    else:
        champions = champions.order_by("name")

    return render(
        request,
        "runeterra/champion_list.html",
        {
            "champions": champions,
            "regions": Region,
        },
    )


class ChampionCreateView(CreateView):
    model = Champion
    form_class = ChampionForm
    template_name = "runeterra/champion_form.html"
    success_url = reverse_lazy("runeterra:champion_list")


class ChampionUpdateView(UpdateView):
    model = Champion
    form_class = ChampionForm
    template_name = "runeterra/champion_form.html"
    success_url = reverse_lazy("runeterra:champion_list")
