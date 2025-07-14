from django.shortcuts import render

from runeterra.models import Champion


def random_picker(request):
    champion = None
    only_unlocked = False
    only_lvl30 = False
    if request.method == "POST":
        only_unlocked = bool(request.POST.get("only_unlocked"))
        only_lvl30 = bool(request.POST.get("only_lvl30"))
        queryset = Champion.objects.all()
        if only_unlocked:
            queryset = queryset.filter(unlocked=True)
        if only_lvl30:
            queryset = queryset.filter(lvl30=True)
        champion = queryset.order_by("?").first()
    return render(
        request,
        "runeterra/random_picker.html",
        {
            "champion": champion,
            "only_unlocked": only_unlocked,
            "only_lvl30": only_lvl30,
        },
    )
