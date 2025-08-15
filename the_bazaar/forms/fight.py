from django import forms

from the_bazaar.models import Fight, Archetype


class FightForm(forms.ModelForm):
    class Meta:
        model = Fight
        fields = ['day_number', 'opponent_character', 'opponent_archetype', 'is_victory', 'comment']
        widgets = {
            'day_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'opponent_character': forms.Select(attrs={'class': 'form-select'}),
            'opponent_archetype': forms.Select(attrs={'class': 'form-select'}),
            'is_victory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }
        labels = {
            'day_number': 'Day',
            'opponent_character': 'Opponent',
            'opponent_archetype': 'Archetype',
            'is_victory': 'Victoire?',
            'comment': 'Comment',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['opponent_archetype'].queryset = Archetype.objects.filter(is_meta_viable=True)
