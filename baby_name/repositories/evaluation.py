from django.contrib.auth.models import User

from baby_name.constants.name_choice import NameChoice
from baby_name.models import Evaluation
from core.repositories.user import UserRepository


class EvaluationRepository:
    @staticmethod
    def get_all_family_positive_vote(user: User):
        family_members = UserRepository.get_family_members(user)
        return Evaluation.objects.filter(
            user__in=family_members,
            score__in=[NameChoice.OUI.value, NameChoice.COUP_DE_COEUR.value]
        )

    @staticmethod
    def get_all_positive_vote_user(user):
        return Evaluation.objects.filter(
            user=user,
            score__in=[NameChoice.OUI.value, NameChoice.COUP_DE_COEUR.value]
        )
