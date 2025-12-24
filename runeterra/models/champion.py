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
    star_level = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(7)])
    champion_level = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(60)])
    monthly_try_remaining = models.IntegerField(
        default=3,
        validators=[MinValueValidator(0), MaxValueValidator(3)],
    )
    unlocked = models.BooleanField(default=False)
    lvl30 = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.set_lvl30()
        super().save(*args, **kwargs)

    def set_lvl30(self):
        if self.champion_level >= 30:
            self.lvl30 = True
        else:
            self.lvl30 = False

    def __str__(self):
        return self.name

    @property
    def monthly_is_available(self):
        return self.monthly_try_remaining > 0 and self.star_level >= 2


@admin.register(Champion)
class ChampionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "primary_region",
        "secondary_region",
        "star_level",
        "monthly_try_remaining",
        "unlocked",
        "lvl30",
    )
    list_filter = ("primary_region", "secondary_region", "unlocked", "lvl30")
    search_fields = ("name",)
