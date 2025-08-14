from django.contrib import admin
from django.db import models

from the_bazaar.constants.character import Character
from the_bazaar.constants.item_size import ItemSize


class Object(models.Model):
    name = models.CharField(max_length=32)
    character = models.CharField(max_length=9, choices=Character.choices)
    size = models.CharField(
        max_length=6,
        choices=ItemSize.choices,
        default=ItemSize.SMALL,
    )
    was_mastered = models.BooleanField(default=False)
    victory_number = models.IntegerField(default=0)

    def __str__(self):
        return self.name


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'character',
        'size',
        'victory_number',
        'was_mastered',
    )
    list_filter = ('character', 'size', 'was_mastered')
    ordering = ('name',)
