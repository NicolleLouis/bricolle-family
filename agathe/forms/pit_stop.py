from django import forms

from agathe.models import PitStop


class PitStopForm(forms.ModelForm):
    class Meta:
        model = PitStop
        fields = ["start_date", "quantity", "comment"]
        widgets = {
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "quantity": forms.NumberInput(attrs={"min": 0, "step": 10}),
            "comment": forms.Textarea(attrs={"rows": 2}),
        }
