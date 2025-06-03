from django.contrib import admin
from django.db import models

from the_bazaar.constants.character import Character


class Object(models.Model):
    name = models.CharField(max_length=32)
    character = models.CharField(max_length=9, choices=Character.choices)
    was_mastered = models.BooleanField(default=False)
    victory_number = models.IntegerField()

    def __str__(self):
        return self.name


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'character', 'victory_number', 'was_mastered')
    list_filter = ('character', 'was_mastered')
    ordering = ('name',)

