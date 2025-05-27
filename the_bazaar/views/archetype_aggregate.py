from django.shortcuts import render

from the_bazaar.models.archetype import Archetype
from the_bazaar.services.aggregate_archetype_run import AggregateArchetypeRunService
from the_bazaar.forms.archetype_filter import ArchetypeFilterForm
from the_bazaar.constants.character import Character
from the_bazaar.constants.result import Result


class BazaarAggregate:
    @staticmethod
    def by_archetype(request):
        filter_form = ArchetypeFilterForm(request.GET)
        range_param = request.GET.get('range', 'current_season')

        if range_param == 'all_time':
            archetypes = Archetype.objects.all().order_by('character', 'name')
        else:  # Default to current_season
            archetypes = Archetype.objects.filter(is_meta_viable=True).order_by('character', 'name')
        
        aggregated_infos = []

        for archetype in archetypes:
            try:
                service = AggregateArchetypeRunService(archetype_id=archetype.id, run_range=range_param)
                aggregated_infos.append(service.result)
            except Exception as e:
                print(f"Error processing archetype {archetype.name} (ID: {archetype.id}): {e}")

        orderby_param = request.GET.get('orderby', 'archetype_name')

        if orderby_param == 'run_number':
            aggregated_infos.sort(key=lambda x: x.run_number, reverse=True)
        else:  # Default to archetype_name or if param is invalid
            aggregated_infos.sort(key=lambda x: x.archetype_name)

        if filter_form.is_valid():
            character_filter = filter_form.cleaned_data.get('character')
            best_result_filter = filter_form.cleaned_data.get('best_result')

            if character_filter:
                aggregated_infos = [
                    info for info in aggregated_infos if info.character_name == Character(character_filter).label
                ]
            
            if best_result_filter:
                expected_best_result_label = Result(best_result_filter).label
                aggregated_infos = [
                    info for info in aggregated_infos if info.best_result == expected_best_result_label
                ]

        context = {
            "aggregated_infos": aggregated_infos,
            "range_options": ["current_season", "all_time"],
            "current_range": range_param,
            "current_orderby": orderby_param,
            "filter_form": filter_form,
        }
        return render(
            request,
            "the_bazaar/aggregated_by_archetype.html",
            context
        )
