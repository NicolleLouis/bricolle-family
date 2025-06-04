from django.contrib import admin
from django.db import models

from the_bazaar.constants.character import Character


class CardSet(models.Model):
    name = models.CharField(max_length=32)
    character = models.CharField(max_length=9, choices=Character.choices, blank=True, null=True)

    def __str__(self):
        return self.name


@admin.register(CardSet)
class CardSetAdmin(admin.ModelAdmin):
    list_display = ("name", "character")
    list_filter = ("character",)
    search_fields = ["name"]
    ordering = ("name",)
