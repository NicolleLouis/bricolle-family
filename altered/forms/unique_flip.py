from django import forms

from altered.constants.faction import Faction


class UniqueFlipPurchaseForm(forms.Form):
    unique_id = forms.CharField(label='Unique ID', max_length=128,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    bought_price = forms.DecimalField(label='Bought price', max_digits=10, decimal_places=2,
                                      widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))


class UniqueFlipSellForm(forms.Form):
    sold_price = forms.DecimalField(label='Sold price', max_digits=10, decimal_places=2,
                                     widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))


class UniqueFlipFilterForm(forms.Form):
    faction = forms.ChoiceField(
        choices=[('', 'All Factions')] + Faction.choices,
        required=False,
        label='Faction',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    hide_zero = forms.BooleanField(
        required=False,
        label='Hide 0 buy price',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

