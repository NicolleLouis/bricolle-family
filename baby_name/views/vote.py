import random

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from baby_name.constants.name_choice import NameChoice
from baby_name.models import Name, Evaluation
from baby_name.repositories.name import NameRepository


class Vote:
    @staticmethod
    def post(request):
        name_id = request.POST.get('name_id')
        score = request.POST.get('score')
        gender_filter = request.POST.get("gender", "all")

        name = get_object_or_404(Name, id=name_id)
        request.session["gender_filter"] = gender_filter

        if score:
            evaluation, _created = Evaluation.objects.get_or_create(
                name=name,
                user=request.user,
            )
            evaluation.score = score
            evaluation.save()
        return redirect("baby_name:interface")

    @classmethod
    def form(cls, request):
        if request.method == "POST":
            gender_filter = request.POST.get("gender", "all")
            request.session["gender_filter"] = gender_filter
        else:
            gender_filter = request.session.get("gender_filter", "all")

        random_name = cls._get_random_name(gender_filter=gender_filter, user=request.user)
        if random_name is None:
            return render(
                request,
                "baby_name/error.html",
                {"message": "No remaining names to vote for."}
            )

        choices = NameChoice.choices
        context = {
            "name": random_name,
            "choices": choices,
            "gender_filter": gender_filter
        }
        return render(request, "baby_name/vote_form.html", context)

    @staticmethod
    def _get_random_name(gender_filter: str, user: User):
        sex = None
        if gender_filter == "boys":
            sex = False
        if gender_filter == "girls":
            sex = True

        if sex is not None:
            priority_names = NameRepository.get_priority_scores(sex=sex, user=user)
            if priority_names.exists():
                return random.choice(priority_names)

        unscored_names = NameRepository.get_unscored_name(gender_filter=gender_filter, user=user)
        if unscored_names.exists():
            return random.choice(unscored_names)

        return None
