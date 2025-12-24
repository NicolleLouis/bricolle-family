import random

from baby_name.exceptions.name_duel import NameDuelException
from baby_name.models import Evaluation
from baby_name.repositories.name import NameRepository


class NameDuel:
    def __init__(self, user, gender_filter: str = "all"):
        self.user = user
        self.sex = self._resolve_sex(user=user, gender_filter=gender_filter)
        self.random_duel = random.choice([True, False])
        self.rankable_names = NameRepository.get_all_rankables_per_user(
            sex=self.sex,
            user=user
        )

    @classmethod
    def _resolve_sex(cls, user, gender_filter: str) -> bool:
        if gender_filter == "boys":
            return False
        if gender_filter == "girls":
            return True
        boys_count = NameRepository.get_all_rankables_per_user(
            sex=False,
            user=user
        ).count()
        girls_count = NameRepository.get_all_rankables_per_user(
            sex=True,
            user=user
        ).count()
        if boys_count < 2 <= girls_count:
            return True
        if girls_count < 2 <= boys_count:
            return False
        return random.choice([True, False])

    def get_names(self):
        if len(self.rankable_names) < 2:
            raise NameDuelException
        if self.random_duel:
            return self.random_names()
        else:
            return self.closest_duel()

    def random_names(self):
        return random.sample(list(self.rankable_names), 2)

    def closest_duel(self):
        name_1 = random.choice(list(self.rankable_names))
        evaluations = Evaluation.objects.filter(name__in=self.rankable_names, user=self.user)
        evaluation_score = {evaluation.name: evaluation.elo for evaluation in evaluations}
        reference_elo = evaluation_score[name_1]
        name_2 = min(
            (name for name in self.rankable_names if name != name_1),
            key=lambda name: abs(evaluation_score[name] - reference_elo)
        )
        return name_1, name_2
