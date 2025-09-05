from django import forms

from civilization7.models import Game


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            "leader",
            "civ_antiquite",
            "civ_exploration",
            "civ_moderne",
            "victory",
            "victory_type",
            "comment",
        ]
