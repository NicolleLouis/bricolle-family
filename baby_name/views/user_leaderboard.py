from django.shortcuts import render

from baby_name.models import Evaluation
from core.repositories.user import UserRepository


def user_leaderboard(request):
    family_members = UserRepository.get_family_members(request.user)
    rankings_boys = {}
    rankings_girls = {}

    for user in family_members:
        rankings_boys[user] = Evaluation.objects.filter(
            user=user,
            name__sex=False,
            elo__gte=1000,
        ).order_by('-elo')[:15]

        rankings_girls[user] = Evaluation.objects.filter(
            user=user,
            name__sex=True,
            elo__gte=1000,
        ).order_by('-elo')[:15]

    context = {
        "rankings_boys": rankings_boys,
        "rankings_girls": rankings_girls,
    }

    return render(request, "baby_name/user_leaderboard.html", context)
