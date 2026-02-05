from django.contrib import admin
from django.db import models


class Dungeon(models.Model):
    name = models.CharField(max_length=100)
    season_apparition = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


@admin.register(Dungeon)
class DungeonAdmin(admin.ModelAdmin):
    list_display = ('name', 'season_apparition')
    search_fields = ["name"]
