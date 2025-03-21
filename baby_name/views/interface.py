import random

from django.shortcuts import render, get_object_or_404

from baby_name.constants.name_choice import NameChoice
from baby_name.models import Name


def interface(request):
    if request.method == "POST":
        gender_filter = request.POST.get("gender", "all")
        request.session["gender_filter"] = gender_filter
    else:
        gender_filter = request.session.get("gender_filter", "all")

    #Sort the available names
    if gender_filter == "boys":
        names_left = Name.objects.filter(sex=False).exclude(evaluation__user=request.user)
    elif gender_filter == "girls":
        names_left = Name.objects.filter(sex=True).exclude(evaluation__user=request.user)
    else:
        names_left = Name.objects.exclude(evaluation__user=request.user)

    if names_left.exists():
        random_name = random.choice(names_left)
        random_id=random_name.id
        name = get_object_or_404(Name, id=random_id)
    else:
        name = None

    choices = NameChoice.choices
    context = {
        "name": name,
        "choices": choices,
        "gender_filter": gender_filter
    }
    return render(request, "baby_name/interface.html", context)
