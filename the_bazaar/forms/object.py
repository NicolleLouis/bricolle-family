from django import forms

from the_bazaar.models import Object


class ObjectForm(forms.ModelForm):
    class Meta:
        model = Object
        fields = [
            'name',
            'character',
            'card_set',
            'size',
            'victory_number',
            'was_mastered',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'character': forms.Select(attrs={'class': 'form-select'}),
            'card_set': forms.Select(attrs={'class': 'form-select'}),
            'size': forms.Select(attrs={'class': 'form-select'}),
            'victory_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'was_mastered': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nom',
            'character': 'Personnage',
            'card_set': 'Card Set',
            'size': 'Taille',
            'victory_number': 'Nombre de victoires',
            'was_mastered': 'Maîtrisé',
        }

