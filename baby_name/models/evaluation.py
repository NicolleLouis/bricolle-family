from django.contrib.auth.models import User
from django.db import models
from django.contrib import admin, messages
from django.utils.translation import ngettext

from baby_name.constants.name_choice import NameChoice
from baby_name.models import Name


class Evaluation(models.Model):
    name = models.ForeignKey(Name, on_delete=models.CASCADE, related_name='evaluations')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.CharField(
        max_length=20,
        choices=NameChoice.choices,
        default=NameChoice.NON
    )
    elo = models.IntegerField(default=1000)
    nb_duels = models.IntegerField(default=0)

    class Meta:
        unique_together = ('name', 'user')

    def __str__(self):
        return f"Note {self.user.username} -> {self.name}"

    def win_game(self, opponent):
        k = 20
        diff = opponent.elo - self.elo
        expected = 1 / (1 + 10 ** (diff / 400))
        delta = round(k * (1 - expected))

        self.elo += delta
        self.nb_duels += 1
        self.save()

    def lose_game(self, opponent):
        k = 20
        diff = opponent.elo - self.elo
        expected = 1 / (1 + 10 ** (diff / 400))
        delta = round(k * (1 - expected))

        self.elo -= delta
        self.nb_duels += 1
        self.save()


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'score', 'elo')
    list_filter = ('user', 'score', 'name__sex')
    search_fields = ["name__name"]
    actions = ["evaluate_negatively"]

    @admin.action(description="Voter Non")
    def evaluate_negatively(self, request, queryset):
        updated = queryset.update(score=NameChoice.NON)
        self.message_user(
            request,
            ngettext(
                "%d name was successfully vetoed :( .",
                "%d names were successfully vetoed :( .",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )
