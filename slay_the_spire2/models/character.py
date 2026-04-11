from django.contrib import admin
from django.db import models


class Character(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)
