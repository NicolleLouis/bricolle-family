from django import forms

from sport.models import TrainingTarget


class TrainingTargetForm(forms.ModelForm):
    class Meta:
        model = TrainingTarget
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Objectif (ex: 5K, Endurance)"}),
        }
