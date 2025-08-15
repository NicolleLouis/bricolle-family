from django import forms

from the_bazaar.constants.character import Character
from the_bazaar.constants.result import Result


class ObjectStatsFilterForm(forms.Form):
    character = forms.ChoiceField(
        choices=[('', 'All Characters')] + Character.choices,
        required=False,
        label='Character',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    victory_type = forms.ChoiceField(
        choices=[
            (Result.GOLD_WIN, 'Gold'),
            (Result.SILVER_WIN, 'Silver'),
            (Result.BRONZE_WIN, 'Bronze'),
        ],
        required=True,
        label='Victory type',
        initial=Result.GOLD_WIN,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
