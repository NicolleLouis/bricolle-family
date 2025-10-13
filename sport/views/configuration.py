from django.shortcuts import redirect, render
from django.urls import reverse

from sport.forms import TrainingForm, TrainingTargetForm
from sport.models import Training, TrainingTarget


def configuration(request):
    target_form = TrainingTargetForm()
    training_form = TrainingForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "target":
            target_form = TrainingTargetForm(request.POST)
            if target_form.is_valid():
                target_form.save()
                return redirect(reverse("sport:configuration"))
        elif form_type == "training":
            training_form = TrainingForm(request.POST)
            if training_form.is_valid():
                training_form.save()
                return redirect(reverse("sport:configuration"))

    context = {
        "target_form": target_form,
        "training_form": training_form,
        "targets": TrainingTarget.objects.order_by("name"),
        "trainings": Training.objects.prefetch_related("training_targets").order_by(
            "name"
        ),
    }
    return render(request, "sport/configuration.html", context)
