from django.shortcuts import render

from the_bazaar.forms.monster_beater import MonsterBeaterForm
from the_bazaar.services.monster_beater import MonsterBeaterService
from the_bazaar.services.monster_finder import MonsterFinderService


class MonsterBeaterView:
    EQUALITY_MESSAGE = "Outcome unclear, Sandstorm will decide"

    @classmethod
    def form(cls, request, monster_name=None):
        result = None
        details = None
        time_to_kill = None
        time_to_death = None
        monster = MonsterFinderService.find_monster(monster_name)

        if request.method == 'POST':
            form = MonsterBeaterForm(request.POST)
            if form.is_valid():
                life = form.cleaned_data['life']
                dps = form.cleaned_data['dps']
                hps = form.cleaned_data['hps']
                pps = form.cleaned_data['pps']
                service = MonsterBeaterService(
                    player_life=life,
                    player_hps=hps,
                    player_dps=dps,
                    player_pps=pps,
                    monster_name=monster_name,
                )
                result = service.result
                if result is None:
                    result = cls.EQUALITY_MESSAGE
                details = service.life_at_sandstorm()
                time_to_kill= service.time_to_kill
                time_to_death= service.time_to_death
        else:
            form = MonsterBeaterForm()

        return render(
            request,
            'the_bazaar/monster_beater.html',
            {
                'form': form,
                'result': result,
                'details': details,
                'time_to_kill': time_to_kill,
                'time_to_death': time_to_death,
                'monster': monster,
            }
        )
