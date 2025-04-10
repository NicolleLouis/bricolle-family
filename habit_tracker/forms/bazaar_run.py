from django import forms

from habit_tracker.models import BazaarRun, BazaarArchetype


class BazaarRunForm(forms.ModelForm):
    class Meta:
        model = BazaarRun
        fields = ['character', 'archetype', 'win_number', 'notes']
        widgets = {
            'character': forms.Select(attrs={'class': 'form-select'}),
            'archetype': forms.Select(attrs={'class': 'form-select'}),
            'win_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de victoire'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Notes'}),
        }
        labels = {
            'character': 'Personnage',
            'archetype': 'Archetype',
            'win_number': 'Nombre de victoire',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archetype'].queryset = BazaarArchetype.objects.filter(is_meta_viable=True)