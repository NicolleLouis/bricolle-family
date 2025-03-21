from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from baby_name.models import Evaluation

class Command(BaseCommand):
    help = "Random stuff"

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            names = self.get_names_evaluated(user)
            for name in names:
                evaluations = Evaluation.objects.filter(user=user, name=name)
                if len(evaluations) > 1:
                    evaluations.exclude(id=evaluations.first().id).delete()

    @staticmethod
    def get_names_evaluated(user: User):
        evaluations = Evaluation.objects.filter(user=user)
        names = []
        for evaluation in evaluations:
            names.append(evaluation.name)
        return list(set(names))
