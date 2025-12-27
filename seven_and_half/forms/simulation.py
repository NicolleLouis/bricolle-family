from django import forms

from seven_and_half.services.deck_service import CardValue


CARD_VALUE_CHOICES = [
    ("random", "Random"),
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


class GameSimulationForm(forms.Form):
    player_card_value = forms.ChoiceField(
        choices=CARD_VALUE_CHOICES,
        label="Carte initiale du joueur",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    bank_card_value = forms.ChoiceField(
        choices=CARD_VALUE_CHOICES,
        label="Carte initiale de la banque",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def clean_player_card_value(self) -> CardValue | None:
        value = self.cleaned_data["player_card_value"]
        if value == "random":
            return None
        return self._parse_card_value(value)

    def clean_bank_card_value(self) -> CardValue | None:
        value = self.cleaned_data["bank_card_value"]
        if value == "random":
            return None
        return self._parse_card_value(value)

    @staticmethod
    def _parse_card_value(value: str) -> CardValue:
        if value == "Joker":
            return value
        if "." in value:
            return float(value)
        return int(value)
