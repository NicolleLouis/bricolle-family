from django.contrib import admin
from django.db import models


class Relic(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


@admin.register(Relic)
class RelicAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)
