from django.shortcuts import render

from the_bazaar.services.fight_character_repartition import FightCharacterRepartitionService
from the_bazaar.services.fight_character_timeseries import FightCharacterTimeseriesService


class MetaView:
    @staticmethod
    def stats(request):
        pie_chart = FightCharacterRepartitionService.generate()
        line_chart = FightCharacterTimeseriesService.generate()
        return render(
            request,
            'the_bazaar/meta.html',
            {
                'pie_chart': pie_chart,
                'line_chart': line_chart,
            }
        )
