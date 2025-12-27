from django.shortcuts import render

from seven_and_half.forms.simulation import GameSimulationForm
from seven_and_half.services.game_simulation_service import GameSimulationService


def game_simulation(request):
    form = GameSimulationForm(request.POST or None)
    result = None
    player_win_percentage = None

    if request.method == "POST" and form.is_valid():
        player_card_value = form.cleaned_data["player_card_value"]
        bank_card_value = form.cleaned_data["bank_card_value"]
        service = GameSimulationService()

        if not service.validate_initial_cards(player_card_value, bank_card_value):
            form.add_error(
                None,
                "Ces cartes de depart ne sont pas disponibles ensemble dans le deck.",
            )
        else:
            result = service.simulate_games(player_card_value, bank_card_value)
            player_win_percentage = round(result.player_win_rate * 100, 2)

    context = {
        "form": form,
        "result": result,
        "player_win_percentage": player_win_percentage,
    }
    return render(request, "seven_and_half/game_simulation.html", context)
