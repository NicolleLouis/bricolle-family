from baby_name.constants.name_choice import NameChoice
from baby_name.models import Evaluation


class EvaluationRepository:
    @staticmethod
    def get_all_positive_vote():
        return Evaluation.objects.filter(
            score__in=[NameChoice.OUI.value, NameChoice.COUP_DE_COEUR.value]
        )
