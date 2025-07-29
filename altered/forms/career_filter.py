from django import forms

from altered.constants.faction import Faction


class CareerFilterForm(forms.Form):
    faction = forms.ChoiceField(
        choices=[('', 'All Factions')] + Faction.choices,
        required=False,
        label='Faction',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    name = forms.CharField(
        required=False,
        label='Champion name',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    only_missing = forms.BooleanField(
        required=False,
        label='Missing only',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
