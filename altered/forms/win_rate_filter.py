from django import forms

from altered.constants.faction import Faction
from altered.constants.win_rate_scope import WinRateScope
from altered.models import Champion, Deck


class WinRateFilterForm(forms.Form):
    scope = forms.ChoiceField(
        choices=WinRateScope.choices,
        required=False,
        initial=WinRateScope.ALL,
        label="Scope",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    faction = forms.ChoiceField(
        choices=[("", "Sélectionnez une faction")] + list(Faction.choices),
        required=False,
        label="Faction",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    champion = forms.ModelChoiceField(
        queryset=Champion.objects.none(),
        required=False,
        label="Champion",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    deck = forms.ModelChoiceField(
        queryset=Deck.objects.none(),
        required=False,
        label="Deck",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    achievement_only = forms.BooleanField(
        required=False,
        label="Achievement only",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["champion"].queryset = Champion.objects.all().order_by("name")
        self.fields["champion"].empty_label = "Sélectionnez un champion"
        self.fields["deck"].queryset = Deck.objects.filter(is_active=True).order_by("name")
        self.fields["deck"].empty_label = "Sélectionnez un deck"

    def clean(self):
        cleaned_data = super().clean()
        scope = cleaned_data.get("scope") or WinRateScope.ALL
        if scope == WinRateScope.FACTION and not cleaned_data.get("faction"):
            self.add_error("faction", "Veuillez choisir une faction.")
        if scope == WinRateScope.CHAMPION and not cleaned_data.get("champion"):
            self.add_error("champion", "Veuillez choisir un champion.")
        if scope == WinRateScope.DECK and not cleaned_data.get("deck"):
            self.add_error("deck", "Veuillez choisir un deck.")
        return cleaned_data
