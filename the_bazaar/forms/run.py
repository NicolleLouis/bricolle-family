from django import forms

from the_bazaar.models import Run


class RunForm(forms.ModelForm):
    class Meta:
        model = Run
        fields = ['character', 'archetype', 'dungeons', 'win_number', 'notes']
        widgets = {
            'character': forms.Select(attrs={'class': 'form-select'}),
            'archetype': forms.Select(attrs={'class': 'form-select'}),
            'dungeons': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'win_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de victoire'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Notes'}),
        }
        labels = {
            'character': 'Personnage',
            'archetype': 'Archetype',
            'dungeons': 'Dungeons',
            'win_number': 'Nombre de victoire',
            'notes': 'Notes',
        }
