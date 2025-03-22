import random

from django.shortcuts import get_object_or_404, render, redirect

from baby_name.models import Name, Evaluation
from baby_name.repositories.name import NameRepository
from baby_name.services.name_duel import NameDuel


class Ranking:
    @staticmethod
    def form(request):
        name_1, name_2 = NameDuel(request.user).get_names()

        context = {
            "name_1": name_1,
            "name_2": name_2,
        }
        return render(request, "baby_name/ranking.html", context)

    @staticmethod
    def post(request):
        winner_id = request.POST.get('winner_id')
        loser_id = request.POST.get('loser_id')

        winner_eval = get_object_or_404(Evaluation, name__id=winner_id, user=request.user)
        loser_eval = get_object_or_404(Evaluation, name__id=loser_id, user=request.user)

        winner_eval.win_game(loser_eval)
        loser_eval.lose_game(winner_eval)

        return redirect('baby_name:ranking')
