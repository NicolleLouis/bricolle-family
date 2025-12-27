from django import forms

from seven_and_half.services.deck_service import CardValue


CARD_VALUE_CHOICES = [
    ("0", "0"),
    ("0.5", "0.5"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
    ("6", "6"),
    ("7", "7"),
    ("Joker", "Joker"),
]


class DrawProbabilityForm(forms.Form):
    initial_card_value = forms.ChoiceField(
        choices=CARD_VALUE_CHOICES,
        label="Carte initiale",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def clean_initial_card_value(self) -> CardValue:
        value = self.cleaned_data["initial_card_value"]
        if value == "Joker":
            return value
        if "." in value:
            return float(value)
        return int(value)
