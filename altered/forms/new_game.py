import json

from django import forms

from altered.constants.faction import Faction
from altered.models import Champion, Deck, Game


class GameForm(forms.ModelForm):
    opponent_faction = forms.ChoiceField(
        choices=[('', 'All factions')] + list(Faction.choices),
        required=False,
        label='Opponent faction',
    )

    class Meta:
        model = Game
        fields = ['deck', 'opponent_champion', 'comment', 'is_win']
        labels = {
            'is_win': 'Victory?',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deck'].queryset = Deck.objects.filter(is_active=True)
        champion_field = self.fields['opponent_champion']
        champion_queryset = Champion.objects.order_by('faction', 'name')
        champion_field.queryset = champion_queryset
        champion_field.widget.attrs['data-champion-factions'] = json.dumps({
            str(champion.pk): champion.faction for champion in champion_queryset
        })
        self.order_fields(['deck', 'opponent_faction', 'opponent_champion', 'comment', 'is_win'])
