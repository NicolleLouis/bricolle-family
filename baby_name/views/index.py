from django.shortcuts import render

from baby_name.models import Name


def index(request):
    name_coup_de_coeur_list = Name.objects.filter(evaluation__score="coup_de_coeur").distinct()

    context = {
        "name_coup_de_coeur_list": name_coup_de_coeur_list
    }
    return render(request, "baby_name/index.html", context)
