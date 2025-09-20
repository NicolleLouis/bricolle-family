from django.shortcuts import render

from altered.constants.win_rate_scope import WinRateScope
from altered.forms.win_rate_filter import WinRateFilterForm
from altered.services.win_rate_stats import WinRateStatsService


def win_rate_view(request):
    if request.GET:
        form = WinRateFilterForm(request.GET)
        if form.is_valid():
            scope = form.cleaned_data.get("scope") or WinRateScope.ALL
            faction = form.cleaned_data.get("faction")
            champion = form.cleaned_data.get("champion")
            deck = form.cleaned_data.get("deck")
            achievement_only = form.cleaned_data.get("achievement_only")
            service = WinRateStatsService(
                scope=scope,
                faction=faction,
                champion=champion,
                deck=deck,
            )
        else:
            service = WinRateStatsService()
            achievement_only = bool(form.data.get("achievement_only"))
    else:
        form = WinRateFilterForm(initial={"scope": WinRateScope.ALL})
        service = WinRateStatsService()
        achievement_only = False

    context = {
        "form": form,
        "stats": service.result,
        "achievement_only": achievement_only,
    }
    return render(request, "altered/win_rate.html", context)
