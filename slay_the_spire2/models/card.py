from django.contrib import admin
from django.db import models


class Card(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)
