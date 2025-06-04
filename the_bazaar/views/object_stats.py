from django.shortcuts import render

from the_bazaar.forms.object_stats_filter import ObjectStatsFilterForm
from the_bazaar.services.aggregate_object_stats import AggregateObjectStatsService


class ObjectStatsView:
    @staticmethod
    def stats(request):
        form = ObjectStatsFilterForm(request.GET)
        character = None
        if form.is_valid():
            character = form.cleaned_data.get('character') or None
        service = AggregateObjectStatsService(character)
        return render(
            request,
            'the_bazaar/object_stats.html',
            {
                'stats': service.result,
                'form': form,
            }
        )
