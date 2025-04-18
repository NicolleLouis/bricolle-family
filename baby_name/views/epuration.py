from django.shortcuts import render

from baby_name.models import Evaluation
from baby_name.repositories.evaluation import EvaluationRepository
from core.repositories.user import UserRepository


def user_epuration(request):
    eval_positive_by_user = EvaluationRepository.get_all_positive_vote_user(request.user)
    name_positive_by_user = [evaluation.name for evaluation in eval_positive_by_user]
    boys_name = [name for name in name_positive_by_user if name.sex is False]
    girls_name = [name for name in name_positive_by_user if name.sex is True]

    family_members = UserRepository.get_family_members(request.user)
    other_user = family_members.exclude(id=request.user.id).first()

    epuration_boys = Evaluation.objects.filter(
        name__in=boys_name,
        user=other_user   
    ).order_by('elo')[:15]

    epuration_girls = Evaluation.objects.filter(
        name__in=girls_name,
        user=other_user   
    ).order_by('elo')[:15]

    context = {
        "epuration_boys": epuration_boys,
        "epuration_girls": epuration_girls,
    }

    return render(request, "baby_name/epuration.html", context)
