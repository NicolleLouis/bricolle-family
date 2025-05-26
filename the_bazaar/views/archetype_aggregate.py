from django.shortcuts import render

from the_bazaar.models.archetype import Archetype
from the_bazaar.services.aggregate_archetype_run import AggregateArchetypeRunService


class BazaarAggregate:
    @staticmethod
    def by_archetype(request):
        range_param = request.GET.get('range', 'current_season')

        archetypes = Archetype.objects.filter(is_meta_viable=True).order_by('character', 'name')
        aggregated_infos = []

        for archetype in archetypes:
            try:
                service = AggregateArchetypeRunService(archetype_id=archetype.id, run_range=range_param)
                aggregated_infos.append(service.result)
            except Exception as e:
                print(f"Error processing archetype {archetype.name} (ID: {archetype.id}): {e}")

        context = {
            "aggregated_infos": aggregated_infos,
            "range_options": ["current_season", "all_time"],
            "current_range": range_param,
        }
        return render(
            request,
            "the_bazaar/aggregated_by_archetype.html",
            context
        )
