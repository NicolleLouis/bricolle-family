from django.shortcuts import render

from habit_tracker.constants.bazaar.character import Character
from habit_tracker.services.bazaar_aggregate_character_run import BazaarAggregateCharacterRunService


class BazaarAggregate:
    @staticmethod
    def by_character(request):
        aggregated_infos = []
        for character in Character.values:
            aggregated_infos.append(BazaarAggregateCharacterRunService(character).result)
        return render(
            request,
            "habit_tracker/bazaar_aggregated_by_character.html",
            {"aggregated_infos": aggregated_infos}
        )
