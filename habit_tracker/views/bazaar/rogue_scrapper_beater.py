from django.shortcuts import render

from habit_tracker.forms.bazaar.rogue_scrapper_beater import RogueScrapperBeaterForm
from habit_tracker.services.bazaar.rogue_scrapper_beater import RogueScrapperBeater


class RogueScrapperBeaterView:
    EQUALITY_MESSAGE = "Outcome unclear, Sandstorm will decide"

    @classmethod
    def form(cls, request):
        result = None

        if request.method == 'POST':
            form = RogueScrapperBeaterForm(request.POST)
            if form.is_valid():
                life = form.cleaned_data['life']
                dps = form.cleaned_data['dps']
                hps = form.cleaned_data['hps']
                result = RogueScrapperBeater(
                    player_life=life,
                    player_hps=hps,
                    player_dps=dps,
                ).result
                if result is None:
                    result = cls.EQUALITY_MESSAGE
        else:
            form = RogueScrapperBeaterForm()

        return render(
            request,
            'habit_tracker/bazaar/rogue_scrapper_beater.html',
            {'form': form, 'result': result}
        )
