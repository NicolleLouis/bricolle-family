from django import forms

class RogueScrapperBeaterForm(forms.Form):
    life = forms.IntegerField(
        required=True,
        label="Life",
        min_value=0,
    )
    dps = forms.DecimalField(
        required=False,
        label="DPS",
        min_value=0,
        max_digits=10,
        decimal_places=1,
    )
    hps = forms.DecimalField(
        required=False,
        label="HPS",
        min_value=0,
        max_digits=10,
        decimal_places=1,
    )
