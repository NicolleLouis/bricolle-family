from django.contrib.auth.models import User
from django.db.models import QuerySet

from baby_name.models import Name, Evaluation
from core.repositories.user import UserRepository


class NameRepository:
    @classmethod
    def get_all_positives_in_family(cls, sex: bool, user: User | None = None):
        if user is None:
            users = []
            names = cls.get_all_family_positive(sex=sex, user=None)
        else:
            users = UserRepository.get_family_members(user)
            names = cls.get_all_family_positive(sex=sex, user=user)
        for member in users:
            evaluated_names = Evaluation.objects.filter(user=member).values('name')
            names = names.filter(id__in=evaluated_names)
        return names

    @classmethod
    def get_all_rankables_per_user(cls, sex: bool, user: User):
        positive_names = cls.get_all_family_positive(sex=sex, user=user)
        linked_evaluations = Evaluation.objects.filter(
            user=user,
            name__in=positive_names
        )
        linked_ids = linked_evaluations.values_list('name_id', flat=True)
        return Name.objects.filter(
            id__in=linked_ids
        )

    @staticmethod
    def get_all_family_positive(sex: bool, user: User | None = None) -> QuerySet:
        from baby_name.repositories.evaluation import EvaluationRepository

        positive_votes = EvaluationRepository.get_all_family_positive_vote(user=user)
        ids = positive_votes.values_list('name_id', flat=True)
        return Name.objects.filter(
            sex=sex,
            id__in=ids
        )

    @classmethod
    def get_priority_to_score(cls, sex: bool, user: User):
        positive_names = cls.get_all_family_positive(sex=sex, user=user)
        all_ids = positive_names.values_list('id', flat=True)
        linked_evaluations = Evaluation.objects.filter(
            user=user,
            name__in=positive_names
        )
        ranked_ids = linked_evaluations.values_list('name_id', flat=True)

        priority_ids = set(all_ids) - set(ranked_ids)
        return Name.objects.filter(
            id__in=priority_ids
        )

    @staticmethod
    def get_unscored_name(gender_filter: str, user: User):
        if gender_filter == "boys":
            return Name.objects.filter(sex=False).exclude(evaluations__user=user)
        elif gender_filter == "girls":
            return Name.objects.filter(sex=True).exclude(evaluations__user=user)
        else:
            return Name.objects.exclude(evaluations__user=user)
