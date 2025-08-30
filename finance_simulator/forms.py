from django import forms


class SimulationForm(forms.Form):
    capital = forms.DecimalField(label="Capital emprunté", min_value=0, decimal_places=2, max_digits=12)
    years = forms.IntegerField(label="Années d'emprunt", min_value=1)
    rate = forms.DecimalField(label="Taux d'emprunt", min_value=0, decimal_places=2, max_digits=5)
