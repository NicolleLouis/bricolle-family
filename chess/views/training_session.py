from django.shortcuts import render, redirect

from chess.forms.training_session import TrainingSessionForm
from chess.models import TrainingSession
from chess.constants.training_type import TrainingType


class TrainingSessionController:
    @staticmethod
    def add_training(request):
        if request.method == "POST":
            form = TrainingSessionForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("chess:training_list")
            else:
                return render(
                    request,
                    "chess/error.html",
                    {"message": "There was an issue while saving this training"},
                )
        else:
            form = TrainingSessionForm()
        return render(request, "chess/add_training.html", {"form": form})

    @staticmethod
    def list_trainings(request):
        training_type = request.GET.get("type")
        trainings = TrainingSession.objects.all()
        if training_type in TrainingType.values:
            trainings = trainings.filter(training_type=training_type)
        trainings = trainings.order_by("-created_at")
        return render(
            request,
            "chess/training_list.html",
            {
                "trainings": trainings,
                "selected_type": training_type,
                "TrainingType": TrainingType,
            },
        )
