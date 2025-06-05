from django import forms

from altered.constants.faction import Faction


class DeckFilterForm(forms.Form):
    faction = forms.ChoiceField(
        choices=[('', 'All Factions')] + Faction.choices,
        required=False,
        label='Faction',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
