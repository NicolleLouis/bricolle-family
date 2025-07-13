from django.contrib import admin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from runeterra.constants.region import Region


class Champion(models.Model):
    name = models.CharField(max_length=255, unique=True)
    region = models.CharField(max_length=20, choices=Region.choices)
    star_level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(6)])
    unlocked = models.BooleanField(default=False)
    lvl30 = models.BooleanField(default=False)

    def __str__(self):
        return self.name


@admin.register(Champion)
class ChampionAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "star_level", "unlocked", "lvl30")
    list_filter = ("region", "unlocked", "lvl30")
    search_fields = ("name",)
