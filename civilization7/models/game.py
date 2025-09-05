from django.contrib import admin
from django.db import models

from civilization7.constants.victoire import Victoire
from civilization7.models.leader import Leader
from civilization7.models.civilization import Civilization


class Game(models.Model):
    leader = models.ForeignKey(Leader, on_delete=models.CASCADE)
    civ_antiquite = models.ForeignKey(
        Civilization, related_name="games_antiquite", on_delete=models.CASCADE
    )
    civ_exploration = models.ForeignKey(
        Civilization, related_name="games_exploration", on_delete=models.CASCADE
    )
    civ_moderne = models.ForeignKey(
        Civilization, related_name="games_moderne", on_delete=models.CASCADE
    )
    victory = models.BooleanField(default=False)
    victory_type = models.CharField(
        max_length=20, choices=Victoire.choices, blank=True, null=True
    )
    comment = models.TextField(blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.leader} - {self.created_at}"


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        "leader",
        "civ_antiquite",
        "civ_exploration",
        "civ_moderne",
        "victory",
        "victory_type",
        "created_at",
    )
    list_filter = ("victory", "victory_type", "leader")
    search_fields = ("leader__name",)
