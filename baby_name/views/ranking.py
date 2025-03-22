import random

from django.shortcuts import get_object_or_404, render, redirect

from baby_name.models import Name, Evaluation
from baby_name.repositories.name import NameRepository


class Ranking:
    @staticmethod
    def form(request):
        sex_to_rank = random.choice([True, False])

        rankable_names = NameRepository.get_all_rankables_per_user(
            sex=sex_to_rank,
            user=request.user
        )

        if len(rankable_names) < 2:
            return render(
                request,
                "baby_name/error.html",
                {"message": "Not enough names to rank."}
            )

        random_name_1, random_name_2 = random.sample(list(rankable_names), 2)
        name_1 = get_object_or_404(Name, id=random_name_1.id)
        name_2 = get_object_or_404(Name, id=random_name_2.id)

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
