import random

from django.core.management.base import BaseCommand

from baby_name.constants.computation_system import ComputationSystem
from baby_name.services.global_ranking import GlobalRanking


class Command(BaseCommand):
    help = "Random stuff"

    def handle(self, *args, **kwargs):
        sex = random.choice([True, False])
        ranking = GlobalRanking(sex=sex, computation_system=ComputationSystem.FLAT)
        ranking.generate_ranking()
        names = ranking.extract_best_name(10)
        print(names)
