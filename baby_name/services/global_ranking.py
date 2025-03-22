from django.contrib.auth.models import User

from baby_name.constants.computation_system import ComputationSystem
from baby_name.exceptions.global_ranking import GlobalRankingException
from baby_name.models import Name, Evaluation
from baby_name.repositories.name import NameRepository


class GlobalRanking:
    def __init__(self, sex: bool, computation_system: str = ComputationSystem.SQUARE):
        self.computation_system = computation_system
        self.users = User.objects.all()
        self.rankable_names = NameRepository.get_all_globally_evaluated(sex=sex).prefetch_related('evaluations')
        self.user_ranked_names = self.generate_user_ranked_names()
        self.ranked_names = {}

    def generate_user_ranked_names(self):
        user_ranked_names = {}
        for user in self.users:
            ordered_names = sorted(
                self.rankable_names,
                key=lambda name: name.evaluations.get(user=user).elo,
                reverse=self.sort_order()
            )
            user_ranked_names[user] = ordered_names
        return user_ranked_names

    def generate_ranking(self):
        for name in self.rankable_names:
            self.ranked_names[name.name] = self.get_name_score(name)

    def sort_order(self):
        return self.computation_system != ComputationSystem.ELO

    def extract_best_name(self, sample_size=10):
        sorted_names = sorted(
            self.ranked_names.items(),
            key=lambda item: item[1],
            reverse=not self.sort_order()
        )
        return sorted_names[:sample_size]

    def get_name_score(self, name: Name):
        score = 0
        for user in self.users:
            score += self.score_per_user(name=name, user=user)
        return score

    def get_name_rank(self, name: Name, user: User):
        return self.user_ranked_names[user].index(name)

    def score_per_user(self, name: Name, user: User) -> int:
        rank = self.get_name_rank(name=name, user=user)
        evaluation = Evaluation.objects.get(
            name=name,
            user=user,
        )
        if self.computation_system == ComputationSystem.FLAT:
            return rank
        elif self.computation_system == ComputationSystem.SQUARE:
            return rank ** 2
        elif self.computation_system == ComputationSystem.ELO:
            return evaluation.elo
        else:
            raise GlobalRankingException("computation system not recognized")
