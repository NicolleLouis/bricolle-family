from django.shortcuts import render

from altered.constants import FACTION_COLORS
from altered.forms.career_filter import CareerFilterForm
from altered.services.career_stats import CareerStatsService


def career_view(request):
    form = CareerFilterForm(request.GET)
    faction = None
    name = None
    only_missing = False
    if form.is_valid():
        faction = form.cleaned_data.get('faction') or None
        name = form.cleaned_data.get('name') or None
        only_missing = form.cleaned_data.get('only_missing')
    service = CareerStatsService(faction=faction, name=name, missing_only=only_missing)
    if only_missing:
        for stat in service.result:
            stat.row_color = FACTION_COLORS.get(stat.champion.faction)
    context = {
        'stats': service.result,
        'form': form,
        'only_missing': only_missing,
    }
    return render(request, 'altered/career.html', context)
