from django.contrib import admin
from django.db import models


class Encounter(models.Model):
    class Type(models.TextChoices):
        ANCIENT = "ancient", "Ancient"
        MONSTER = "monster", "Monster"
        ROOM = "room", "Room"
        ELITE = "elite", "Elite"
        BOSS = "boss", "Boss"
        REST_SITE = "rest_site", "RestSite"
        TREASURE = "treasure", "Treasure"

    type = models.CharField(max_length=20, choices=Type.choices)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.get_type_display()} - {self.name}"


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "name")
    list_filter = ("type",)
    search_fields = ("name",)
    ordering = ("type", "name")
