from django.shortcuts import render

from habit_tracker.constants.bazaar.character import Character
from habit_tracker.services.bazaar.aggregate_character_run import AggregateCharacterRunService
from habit_tracker.services.bazaar.character_run_repartition import CharacterRunRepartitionService


class BazaarAggregate:
    @staticmethod
    def by_character(request):
        range_param = request.GET.get('range', 'current_season')

        aggregated_infos = []
        for character in Character.values:
            aggregated_infos.append(
                AggregateCharacterRunService(character, range_param).result
            )

        character_repartition_chart = CharacterRunRepartitionService.generate(range_param)

        return render(
            request,
            "habit_tracker/bazaar/aggregated_by_character.html",
            {
                "aggregated_infos": aggregated_infos,
                "range_options": ["current_season", "all_time"],
                "chart": character_repartition_chart
            }
        )
