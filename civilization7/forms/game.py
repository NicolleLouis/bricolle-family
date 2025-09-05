from django import forms

from civilization7.models import Game


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            "leader",
            "ancient_civ",
            "exploration_civ",
            "modern_civ",
            "victory",
            "victory_type",
            "comment",
        ]
