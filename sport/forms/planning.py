from django import forms

from sport.models import Training


class PlanningForm(forms.Form):
    WEEKDAY_CHOICES = [
        ("0", "Lundi"),
        ("1", "Mardi"),
        ("2", "Mercredi"),
        ("3", "Jeudi"),
        ("4", "Vendredi"),
        ("5", "Samedi"),
        ("6", "Dimanche"),
    ]

    training = forms.ModelChoiceField(
        queryset=Training.objects.none(), label="Entraînement"
    )
    weekday = forms.ChoiceField(choices=WEEKDAY_CHOICES, label="Jour de la semaine")
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Date de début",
    )
    weeks_count = forms.IntegerField(
        min_value=1,
        label="Nombre de semaines",
        widget=forms.NumberInput(attrs={"min": 1, "value": 4}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["training"].queryset = Training.objects.order_by("name")
