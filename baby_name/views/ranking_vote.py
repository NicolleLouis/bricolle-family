from django.shortcuts import get_object_or_404, redirect

from baby_name.models import Evaluation


def ranking_vote(request):
    winner_id = request.POST.get('winner_id')
    loser_id = request.POST.get('loser_id')

    winner_eval = get_object_or_404(Evaluation, name__id = winner_id, user=request.user)
    loser_eval = get_object_or_404(Evaluation, name__id = loser_id, user=request.user)

    winner_eval.win_game(loser_eval)
    loser_eval.lose_game(winner_eval)

    return redirect('baby_name:ranking')
