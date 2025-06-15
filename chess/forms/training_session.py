from django import forms

from chess.models import TrainingSession


class TrainingSessionForm(forms.ModelForm):
    class Meta:
        model = TrainingSession
        fields = ["training_type", "elo", "comment"]
        widgets = {
            "training_type": forms.Select(attrs={"class": "form-select"}),
            "elo": forms.NumberInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "training_type": "Type",
            "elo": "Elo",
            "comment": "Commentaire",
        }
