from django.shortcuts import get_object_or_404, redirect

from baby_name.models import Name, Evaluation


def vote(request):
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
