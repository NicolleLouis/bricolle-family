from django import forms

from agathe.models import PitStop


class PitStopForm(forms.ModelForm):
    class Meta:
        model = PitStop
        fields = ["start_date", "end_date", "side"]
        widgets = {
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
