from django import forms

from agathe.models import PitStop


class PitStopForm(forms.ModelForm):
    class Meta:
        model = PitStop
        fields = ["side"]
