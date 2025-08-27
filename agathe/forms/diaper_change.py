from django import forms

from agathe.models import DiaperChange


class DiaperChangeForm(forms.ModelForm):
    class Meta:
        model = DiaperChange
        fields = ["urine", "pooh"]
        labels = {"pooh": "Caca"}
