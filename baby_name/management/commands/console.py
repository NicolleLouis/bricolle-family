import time

from django.core.management.base import BaseCommand

from baby_name.constants.computation_system import ComputationSystem
from baby_name.services.global_ranking import GlobalRanking


class Command(BaseCommand):
    help = "Random stuff"

    def handle(self, *args, **kwargs):
        start_time = time.time()
        rankings = {True: {}, False: {}}
        scoring_system = [
            ComputationSystem.SQUARE,
            ComputationSystem.FLAT,
            ComputationSystem.ELO,
        ]
        for sex in [True, False]:
            for system in scoring_system:
                ranking = GlobalRanking(
                    sex=sex,
                    computation_system=system
                )
                ranking.generate_ranking()
                names = ranking.extract_best_name(10)
                rankings[sex][system.value] = names
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")