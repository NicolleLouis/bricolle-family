from django import forms

from flash_cards.models import ThemePreset


class ThemePresetForm(forms.ModelForm):
    class Meta:
        model = ThemePreset
        fields = ["name", "is_exclusion", "categories"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom du preset",
                }
            ),
            "is_exclusion": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "categories": forms.SelectMultiple(
                attrs={"class": "form-select", "size": "8"}
            ),
        }
