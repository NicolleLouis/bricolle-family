from django.shortcuts import render

from the_bazaar.forms.object_stats_filter import ObjectStatsFilterForm
from the_bazaar.services.aggregate_object_stats import AggregateObjectStatsService
from the_bazaar.constants.result import Result


class ObjectStatsView:
    @staticmethod
    def stats(request):
        form = ObjectStatsFilterForm(request.GET or None)
        character = None
        victory_type = Result.GOLD_WIN
        if form.is_valid():
            character = form.cleaned_data.get('character') or None
            victory_type = form.cleaned_data.get('victory_type')
        service = AggregateObjectStatsService(character, victory_type)
        return render(
            request,
            'the_bazaar/object_stats.html',
            {
                'stats': service.result,
                'form': form,
            }
        )
