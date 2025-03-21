from django.shortcuts import render

from baby_name.models import Name


def results(request):
    name_coup_de_coeur_list_boys = Name.objects.filter(
        evaluation__score="coup_de_coeur",
        evaluation__user=request.user,
        sex=False
    ).distinct()

    name_coup_de_coeur_list_girls = Name.objects.filter(
        evaluation__score="coup_de_coeur",
        evaluation__user=request.user,
        sex=True
    ).distinct()

    name_yes_list_boys = Name.objects.filter(
        evaluation__score="oui",
        evaluation__user=request.user,
        sex=False
    ).distinct()
    name_yes_list_girls = Name.objects.filter(
        evaluation__score="oui",
        evaluation__user=request.user,
        sex=True
    ).distinct()

    context = {
        "name_coup_de_coeur_list_boys": name_coup_de_coeur_list_boys,
        "name_coup_de_coeur_list_girls": name_coup_de_coeur_list_girls,
        "name_yes_list_boys": name_yes_list_boys,
        "name_yes_list_girls": name_yes_list_girls,
    }
    return render(request, "baby_name/results.html", context)
