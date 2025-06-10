from django import forms

from altered.constants.duration import Duration


class MetaStatsFilterForm(forms.Form):
    duration = forms.ChoiceField(
        choices=Duration.choices,
        required=False,
        label='Duration',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
