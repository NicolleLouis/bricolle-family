from django.contrib.auth.models import User

from baby_name.models import Name, Evaluation


class UserRanking:
    @staticmethod
    def get_name_position(user: User, name: Name):
        all_evaluations = Evaluation.objects.filter(user=user, name__sex=name.sex).order_by('-elo')
        try:
            evaluation = Evaluation.objects.get(user=user, name=name)
        except Evaluation.DoesNotExist:
            return None
        return list(all_evaluations).index(evaluation) + 1
