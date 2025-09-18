from django import forms

from silksong.constants import GameSessionType
from silksong.models import GameSession


class BaseGameSessionForm(forms.ModelForm):
    session_type = None

    class Meta:
        model = GameSession
        fields = []

    def save(self, commit=True):
        if self.session_type is None:
            raise ValueError("session_type must be defined on subclasses")
        self.instance.type = self.session_type
        return super().save(commit=commit)


class SpeedrunGameSessionForm(BaseGameSessionForm):
    session_type = GameSessionType.SPEEDRUN

    class Meta(BaseGameSessionForm.Meta):
        fields = ["duration", "death_number"]


class SteelSoulGameSessionForm(BaseGameSessionForm):
    session_type = GameSessionType.STEEL_SOUL

    class Meta(BaseGameSessionForm.Meta):
        fields = ["victory", "death_explanation"]


class BossFightGameSessionForm(BaseGameSessionForm):
    session_type = GameSessionType.BOSS_FIGHT

    class Meta(BaseGameSessionForm.Meta):
        fields = ["boss", "death_number"]
