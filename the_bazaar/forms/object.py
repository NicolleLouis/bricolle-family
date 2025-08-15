from django import forms

from the_bazaar.models import Object


class ObjectForm(forms.ModelForm):
    class Meta:
        model = Object
        fields = [
            'name',
            'character',
            'size',
            'bronze_win_number',
            'silver_win_number',
            'gold_win_number',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'character': forms.Select(attrs={'class': 'form-select'}),
            'size': forms.Select(attrs={'class': 'form-select'}),
            'bronze_win_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'silver_win_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'gold_win_number': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nom',
            'character': 'Personnage',
            'size': 'Taille',
            'bronze_win_number': 'Bronze wins',
            'silver_win_number': 'Silver wins',
            'gold_win_number': 'Gold wins',
        }

