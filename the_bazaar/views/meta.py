from django.shortcuts import render

from the_bazaar.services.fight_character_repartition import FightCharacterRepartitionService
from the_bazaar.services.fight_character_timeseries import FightCharacterTimeseriesService


class MetaView:
    @staticmethod
    def stats(request):
        character_total_repartition = FightCharacterRepartitionService.generate()
        daily_repartition = FightCharacterTimeseriesService.generate()
        return render(
            request,
            'the_bazaar/meta.html',
            {
                'character_total_repartition': character_total_repartition,
                'daily_repartition': daily_repartition,
            }
        )
