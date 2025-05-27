from django import forms
from the_bazaar.constants.character import Character
from the_bazaar.constants.result import Result

class ArchetypeFilterForm(forms.Form):
    character = forms.ChoiceField(
        choices=[('', 'All Characters')] + Character.choices,
        required=False,
        label="Character",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    best_result = forms.ChoiceField(
        choices=[('', 'All Results')] + Result.choices,
        required=False,
        label="Best Result",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
