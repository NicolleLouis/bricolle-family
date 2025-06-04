from django import forms

from the_bazaar.constants.character import Character


class ObjectStatsFilterForm(forms.Form):
    character = forms.ChoiceField(
        choices=[('', 'All Characters')] + Character.choices,
        required=False,
        label='Character',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
