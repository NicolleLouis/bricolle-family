from django.shortcuts import render

from baby_name.constants.computation_system import ComputationSystem
from baby_name.services.global_ranking import GlobalRanking


def global_leaderboard(request):
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

    print(rankings)

    context = {
        'male_rankings': rankings[False],
        'female_rankings': rankings[True],
    }

    return render(request, "baby_name/global_leaderboard.html", context)
