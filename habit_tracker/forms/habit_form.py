from django import forms

from habit_tracker.models import Habit
from habit_tracker.models.choices import CheckFrequency


class HabitUpdateForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ("check_frequency", "objective_in_frequency")
        labels = {
            "check_frequency": "Fréquence de vérification",
            "objective_in_frequency": "Nombre de validations",
        }
        widgets = {
            "check_frequency": forms.Select(attrs={"class": "form-select"}),
            "objective_in_frequency": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 6}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        frequency = cleaned_data.get("check_frequency")
        objective_in_frequency = cleaned_data.get("objective_in_frequency")

        if frequency == CheckFrequency.DAILY:
            cleaned_data["objective_in_frequency"] = 1
            self.instance.objective_in_frequency = 1
        elif frequency == CheckFrequency.WEEKLY:
            if objective_in_frequency is None:
                self.add_error(
                    "objective_in_frequency", "Veuillez saisir un nombre entre 1 et 6."
                )
            elif not 1 <= objective_in_frequency <= 6:
                self.add_error(
                    "objective_in_frequency",
                    "Doit être compris entre 1 et 6 pour une fréquence hebdomadaire.",
                )
        return cleaned_data
