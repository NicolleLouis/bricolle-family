from django import forms

from baby_name.models import Name


class NameForm(forms.ModelForm):
    class Meta:
        model = Name
        fields = [
            'name',
            'sex',
            'tag',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'sex': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Breton, Traditionnel...'}),
        }
        labels = {
            'name': 'Nom',
            'sex': 'Sexe (Oui pour une fille)',
            'tag': 'Tag (Optionnel)',
        }
