from django.shortcuts import render

from altered.forms.meta_stats_filter import MetaStatsFilterForm
from altered.services.meta_game_stats import MetaGameStatsService
from altered.constants.duration import Duration


def meta_stats_view(request):
    form = MetaStatsFilterForm(request.GET)
    duration = Duration.ALL
    if form.is_valid():
        duration = form.cleaned_data.get('duration') or Duration.ALL
    service = MetaGameStatsService(duration)
    return render(request, 'altered/meta_stats.html', {'stats': service.result, 'form': form})

