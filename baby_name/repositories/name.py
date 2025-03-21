from django.contrib.auth.models import User

from baby_name.models import Name, Evaluation


class NameRepository:
    @classmethod
    def get_all_rankable_names(cls, sex: bool, user: User):
        positive_names = cls.get_all_positive_names(sex=sex)
        linked_evaluations = Evaluation.objects.filter(
            user=user,
            name__in=positive_names
        )
        linked_ids = linked_evaluations.values_list('name_id', flat=True)
        return Name.objects.filter(
            id__in=linked_ids
        )

    @staticmethod
    def get_all_positive_names(sex: bool):
        from baby_name.repositories.evaluation import EvaluationRepository

        positive_votes = EvaluationRepository.get_all_positive_vote()
        ids = positive_votes.values_list('name_id', flat=True)
        return Name.objects.filter(
            sex=sex,
            id__in=ids
        )
