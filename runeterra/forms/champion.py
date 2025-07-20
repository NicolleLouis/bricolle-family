from django import forms

from runeterra.models import Champion
from runeterra.constants.region import Region


class ChampionForm(forms.ModelForm):
    class Meta:
        model = Champion
        fields = [
            "name",
            "primary_region",
            "secondary_region",
            "star_level",
            "champion_level",
            "unlocked",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "primary_region": forms.Select(attrs={"class": "form-select"}),
            "secondary_region": forms.Select(attrs={"class": "form-select"}),
            "star_level": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 6}),
            "champion_level": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 60}),
            "unlocked": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "name": "Name",
            "primary_region": "Primary region",
            "secondary_region": "Secondary region",
            "star_level": "Star level",
            "champion_level": "Level",
            "unlocked": "Unlocked",
        }

