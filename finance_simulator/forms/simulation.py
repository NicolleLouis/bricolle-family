from django import forms


class SimulationForm(forms.Form):
    house_cost = forms.DecimalField(label="Prix du bien", min_value=0, decimal_places=2, max_digits=12)
    initial_contribution = forms.DecimalField(label="Apport initial", min_value=0, decimal_places=2, max_digits=12)
    years = forms.IntegerField(label="Années d'emprunt", min_value=1)
    rate = forms.DecimalField(label="Taux d'emprunt", min_value=0, decimal_places=2, max_digits=5)
    comparative_rent = forms.DecimalField(
        label="Loyer actuel (optionnel)",
        min_value=0,
        decimal_places=2,
        max_digits=12,
        required=False,
    )
