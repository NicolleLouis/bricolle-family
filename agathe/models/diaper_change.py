from django.contrib import admin
from django.db import models


class DiaperChange(models.Model):
    date = models.DateTimeField()


@admin.register(DiaperChange)
class DiaperChangeAdmin(admin.ModelAdmin):
    list_display = ("date",)
    ordering = ("-date",)
