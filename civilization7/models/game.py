from django.contrib import admin
from django.db import models

from civilization7.constants.victory import Victory
from civilization7.models.leader import Leader
from civilization7.models.civilization import Civilization


class Game(models.Model):
    leader = models.ForeignKey(Leader, on_delete=models.CASCADE, verbose_name="Leader")
    ancient_civ = models.ForeignKey(
        Civilization,
        related_name="games_ancient",
        on_delete=models.CASCADE,
        verbose_name="Antiquité",
    )
    exploration_civ = models.ForeignKey(
        Civilization,
        related_name="games_exploration",
        on_delete=models.CASCADE,
        verbose_name="Exploration",
    )
    modern_civ = models.ForeignKey(
        Civilization,
        related_name="games_modern",
        on_delete=models.CASCADE,
        verbose_name="Moderne",
    )
    victory = models.BooleanField(default=False, verbose_name="Victoire")
    victory_type = models.CharField(
        max_length=20,
        choices=Victory.choices,
        blank=True,
        null=True,
        verbose_name="Type de victoire",
    )
    comment = models.TextField(blank=True, verbose_name="Commentaire")
    created_at = models.DateField(auto_now_add=True, verbose_name="Date")

    def __str__(self):
        return f"{self.leader} - {self.created_at}"


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        "leader",
        "ancient_civ",
        "exploration_civ",
        "modern_civ",
        "victory",
        "victory_type",
        "created_at",
    )
    list_filter = ("victory", "victory_type", "leader")
    search_fields = ("leader__name",)
