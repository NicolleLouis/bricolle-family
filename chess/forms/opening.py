from django import forms

from chess.models import Opening


class OpeningForm(forms.ModelForm):
    class Meta:
        model = Opening
        fields = ["name"]
        labels = {
            "name": "Nom",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom de l'ouverture",
                }
            ),
        }
