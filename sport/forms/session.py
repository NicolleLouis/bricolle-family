from django import forms

from sport.models import Session


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["training", "date"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
