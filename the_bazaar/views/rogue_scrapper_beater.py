from django.shortcuts import render

from the_bazaar.forms.monster_beater import MonsterBeaterForm
from the_bazaar.services.monster_beater import MonsterBeaterService


class RogueScrapperBeaterView:
    EQUALITY_MESSAGE = "Outcome unclear, Sandstorm will decide"

    @classmethod
    def form(cls, request):
        result = None

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
                )
                result = service.result
                if result is None:
                    result = cls.EQUALITY_MESSAGE
                details = service.life_at_sandstorm()
        else:
            form = MonsterBeaterForm()

        return render(
            request,
            'the_bazaar/rogue_scrapper_beater.html',
            {'form': form, 'result': result, 'details': details}
        )
