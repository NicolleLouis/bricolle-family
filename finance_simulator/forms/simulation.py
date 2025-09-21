from django import forms

from ..models import Simulation


class SimulationForm(forms.ModelForm):
    house_cost = forms.DecimalField(label="Prix du bien", min_value=0, decimal_places=2, max_digits=12)
    initial_contribution = forms.DecimalField(
        label="Apport initial (€)",
        min_value=0,
        decimal_places=2,
        max_digits=12,
    )
    duration = forms.IntegerField(label="Années d'emprunt", min_value=1)
    annual_rate = forms.DecimalField(label="Taux d'emprunt (%)", min_value=0, decimal_places=2, max_digits=5)
    notary_fees = forms.ChoiceField(
        label="Frais de notaire",
        choices=Simulation.NOTARY_FEES_CHOICES,
        initial=Simulation.NOTARY_FEES_NO,
    )
    comparative_rent = forms.DecimalField(
        label="Loyer actuel (€/Mois)",
        min_value=0,
        decimal_places=2,
        max_digits=12,
        required=False,
    )
    duration_before_usable = forms.IntegerField(
        label="Achat sur Plan: Nombre de mois avant livraison",
        min_value=0,
        required=False,
    )
    use_real_estate_firm = forms.BooleanField(
        label="Vente par cabinet immobilier",
        initial=True,
        required=False,
    )
    sell_price_change = forms.DecimalField(
        label="Changement de valeur du bien (%)",
        required=False,
    )
    monthly_expenses = forms.DecimalField(
        label="Charge Mensuelle (€/Mois)",
        min_value=0,
        decimal_places=2,
        max_digits=12,
        required=False,
    )
    property_tax = forms.DecimalField(
        label="Taxe foncière (€/Année)",
        min_value=0,
        decimal_places=2,
        max_digits=12,
        required=False,
    )

    class Meta:
        model = Simulation
        fields = [
            "house_cost",
            "initial_contribution",
            "duration",
            "annual_rate",
            "notary_fees",
            "comparative_rent",
            "duration_before_usable",
            "use_real_estate_firm",
            "sell_price_change",
            "monthly_expenses",
            "property_tax",
        ]
