from django import forms

from core.models.family import Family


class MassYesForm(forms.Form):
    names = forms.CharField(
        label="Liste de prénoms",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "Un prénom par ligne, ou séparé par des virgules.",
            }
        ),
    )
    family = forms.ModelChoiceField(
        label="Famille",
        queryset=Family.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["family"].queryset = Family.objects.order_by("name")
