from django.contrib import admin
from django.db import models

from the_bazaar.constants.character import Character
from the_bazaar.constants.item_size import ItemSize
from the_bazaar.constants.result import Result


class Object(models.Model):
    name = models.CharField(max_length=32)
    character = models.CharField(
        max_length=9,
        choices=Character.choices,
        null=True,
        blank=True,
    )
    size = models.CharField(
        max_length=6,
        choices=ItemSize.choices,
        default=ItemSize.SMALL,
    )
    best_win = models.CharField(
        max_length=10,
        choices=Result.choices,
        null=True,
        blank=True,
    )
    bronze_win_number = models.IntegerField(default=0)
    silver_win_number = models.IntegerField(default=0)
    gold_win_number = models.IntegerField(default=0)

    def _determine_best_win(self):
        if self.gold_win_number > 0:
            return Result.GOLD_WIN
        if self.silver_win_number > 0:
            return Result.SILVER_WIN
        if self.bronze_win_number > 0:
            return Result.BRONZE_WIN
        return None

    def save(self, *args, **kwargs):
        # Keep best_win consistent with the stored victory counters.
        self.best_win = self._determine_best_win()
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            update_fields = set(update_fields)
            update_fields.add('best_win')
            kwargs['update_fields'] = list(update_fields)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'character',
        'size',
        'gold_win_number',
        'silver_win_number',
        'bronze_win_number',
        'best_win',
    )
    list_filter = ('character', 'size', 'best_win')
    ordering = ('name',)
