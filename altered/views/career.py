from django.shortcuts import render

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
    context = {
        'stats': service.result,
        'form': form,
    }
    return render(request, 'altered/career.html', context)
