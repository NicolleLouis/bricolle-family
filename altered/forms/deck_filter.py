from django import forms

from altered.constants.faction import Faction


class DeckFilterForm(forms.Form):
    faction = forms.ChoiceField(
        choices=[('', 'All Factions')] + Faction.choices,
        required=False,
        label='Faction',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    only_active = forms.BooleanField(
        required=False,
        label='Active deck only',
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
