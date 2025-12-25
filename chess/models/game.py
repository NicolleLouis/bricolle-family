from django.contrib import admin
from django.db import models

from chess.models import Opening


class Game(models.Model):
    COLOR_WHITE = 'white'
    COLOR_BLACK = 'black'
    COLOR_CHOICES = [
        (COLOR_WHITE, 'Blanc'),
        (COLOR_BLACK, 'Noir'),
    ]

    url = models.URLField(max_length=500)
    pgn = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=5, choices=COLOR_CHOICES)
    opening = models.ForeignKey(Opening, on_delete=models.PROTECT, related_name='games')
    lessons = models.TextField()

    def __str__(self):
        return f"{self.get_color_display()} - {self.opening.name}"


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('opening', 'color', 'url')
    list_filter = ('color', 'opening')
    search_fields = ('url', 'pgn', 'lessons', 'opening__name')
