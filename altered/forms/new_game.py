from django import forms

from altered.models import Game, Deck


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['deck', 'opponent_champion', 'comment', 'is_win']
        labels = {
            'is_win': 'Victory?',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deck'].queryset = Deck.objects.filter(is_active=True)
