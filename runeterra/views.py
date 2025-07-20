from django.db.models import Avg, Case, F, IntegerField, Q, When
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from runeterra.models import Champion
from runeterra.constants.region import Region
from runeterra.forms.champion import ChampionForm


def random_picker(request):
    champion = None
    only_unlocked = False
    only_lvl30 = False
    selected_region = ""
    min_star_level = 0

    if request.method == "POST":
        only_unlocked = bool(request.POST.get("only_unlocked"))
        only_lvl30 = bool(request.POST.get("only_lvl30"))
        selected_region = request.POST.get("region", "")
        try:
            min_star_level = int(request.POST.get("min_star_level", 0))
        except (TypeError, ValueError):
            min_star_level = 0

        queryset = Champion.objects.all()

        if only_unlocked:
            queryset = queryset.filter(unlocked=True)
        if only_lvl30:
            queryset = queryset.filter(lvl30=True)
        if selected_region:
            queryset = queryset.filter(
                Q(primary_region=selected_region)
                | Q(secondary_region=selected_region)
            )
        if min_star_level:
            queryset = queryset.filter(star_level__gte=min_star_level)

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
            "regions": Region,
        },
    )


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


def region_stats(request):
    stats = []
    for value, label in Region.choices:
        qs = Champion.objects.filter(Q(primary_region=value) | Q(secondary_region=value))
        total = qs.count()
        unlocked = qs.filter(unlocked=True).count()
        avg = (
            qs.annotate(
                effective=F("star_level")
                + Case(When(lvl30=True, then=1), default=0, output_field=IntegerField())
            )
            .aggregate(avg=Avg("effective"))
            .get("avg")
            or 0
        )
        stats.append({"label": label, "total": total, "unlocked": unlocked, "avg": avg})

    return render(request, "runeterra/region_stats.html", {"stats": stats})
