import random

from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404, render

from baby_name.models import Name, Evaluation


def ranking(request):
    sex_to_rank = random.choice([True, False])

    user_evaluated_names = Name.objects.filter(
        sex=sex_to_rank,
        evaluation__user=request.user
    ).distinct()

    ranking_names = user_evaluated_names.filter(
        Exists(
            Evaluation.objects.filter(
                name=OuterRef('pk'),
                score__in=["oui", "coup_de_coeur"]
            )
        )
    )

    # Randomly picks two names
    if ranking_names.exists():
        random_name_1 = random.choice(ranking_names)
        ranking_names = ranking_names.exclude(id=random_name_1.id)
        random_name_2 = random.choice(ranking_names)
        (random_id_1, random_id_2) = (random_name_1.id, random_name_2.id)
        name_1 = get_object_or_404(Name, id=random_id_1)
        name_2 = get_object_or_404(Name, id=random_id_2)
    else:
        name_1 = None
        name_2 = None

        # Context
    context = {
        "name_1": name_1,
        "name_2": name_2,
    }
    return render(request, "baby_name/ranking.html", context)