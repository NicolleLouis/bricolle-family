from django import forms

from chess.models import Game, Opening


class GameForm(forms.ModelForm):
    opening = forms.ModelChoiceField(
        queryset=Opening.objects.order_by("name"),
        empty_label="Choisir une ouverture",
        label="Ouverture",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Game
        fields = ["url", "pgn", "color", "opening", "lessons"]
        labels = {
            "url": "Lien de la partie",
            "pgn": "PGN",
            "color": "Couleur",
            "lessons": "Lecons",
        }
        widgets = {
            "url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://lichess.org/...",
                }
            ),
            "pgn": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "PGN (optionnel)",
                }
            ),
            "color": forms.Select(attrs={"class": "form-select"}),
            "lessons": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Lecons apprises...",
                }
            ),
        }
