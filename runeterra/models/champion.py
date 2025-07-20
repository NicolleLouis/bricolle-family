from django.contrib import admin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from runeterra.constants.region import Region


class Champion(models.Model):
    name = models.CharField(max_length=255, unique=True)
    primary_region = models.CharField(max_length=20, choices=Region.choices)
    secondary_region = models.CharField(
        max_length=20, choices=Region.choices, blank=True, null=True
    )
    star_level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(6)])
    unlocked = models.BooleanField(default=False)
    lvl30 = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def effective_star_level(self):
        if self.lvl30:
            return self.star_level + 1
        return self.star_level


@admin.register(Champion)
class ChampionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "primary_region",
        "secondary_region",
        "star_level",
        "unlocked",
        "lvl30",
    )
    list_filter = ("primary_region", "secondary_region", "unlocked", "lvl30")
    search_fields = ("name",)
