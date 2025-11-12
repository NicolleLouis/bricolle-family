from django.shortcuts import render

from altered.forms.meta_stats_filter import MetaStatsFilterForm
from altered.services.meta_game_stats import MetaGameStatsService
from altered.services.opponent_faction_chart import OpponentFactionChartService
from altered.constants.duration import Duration


def meta_stats_view(request):
    form = MetaStatsFilterForm(request.GET)
    duration = Duration.ALL
    if form.is_valid():
        duration = form.cleaned_data.get('duration') or Duration.ALL
    service = MetaGameStatsService(duration)
    faction_chart = OpponentFactionChartService(service.result).render()
    context = {
        'stats': service.result,
        'form': form,
        'faction_chart': faction_chart,
    }
    return render(request, 'altered/meta_stats.html', context)
