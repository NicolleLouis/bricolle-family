from urllib.parse import urlencode

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from baby_name.exceptions.name_duel import NameDuelException
from baby_name.models import Evaluation
from baby_name.services.name_duel import NameDuel


class Ranking:
    @staticmethod
    def form(request):
        try:
            gender_filter = request.GET.get("gender", "all")
            name_1, name_2 = NameDuel(
                request.user,
                gender_filter=gender_filter
            ).get_names()
        except NameDuelException as exception:
            return render(
                request,
                "baby_name/error.html",
            {"message": "Moins de 2 prénoms ont été choisis, retournez en ajouter"}
            )

        context = {
            "name_1": name_1,
            "name_2": name_2,
            "gender_filter": gender_filter,
        }
        return render(request, "baby_name/ranking.html", context)

    @staticmethod
    def post(request):
        winner_id = request.POST.get('winner_id')
        loser_id = request.POST.get('loser_id')
        gender_filter = request.POST.get("gender", "all")

        winner_eval = get_object_or_404(Evaluation, name__id=winner_id, user=request.user)
        loser_eval = get_object_or_404(Evaluation, name__id=loser_id, user=request.user)

        winner_eval.win_game(loser_eval)
        loser_eval.lose_game(winner_eval)

        query = urlencode({"gender": gender_filter})
        return redirect(f"{reverse('baby_name:ranking')}?{query}")
