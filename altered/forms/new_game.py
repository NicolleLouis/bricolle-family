from django import forms

from altered.models import Game


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['deck', 'opponent_champion', 'comment', 'is_win']
        labels = {
            'is_win': 'Victory?',
        }
