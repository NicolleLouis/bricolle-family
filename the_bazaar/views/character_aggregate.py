from django.shortcuts import render

from the_bazaar.constants.character import Character
from the_bazaar.services.aggregate_character_run import AggregateCharacterRunService
from the_bazaar.services.character_run_repartition import CharacterRunRepartitionService


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
            "the_bazaar/aggregated_by_character.html",
            {
                "aggregated_infos": aggregated_infos,
                "range_options": ["current_season", "all_time"],
                "chart": character_repartition_chart
            }
        )
