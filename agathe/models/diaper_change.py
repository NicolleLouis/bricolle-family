from django.contrib import admin
from django.db import models


class DiaperChange(models.Model):
    date = models.DateTimeField()
    urine = models.BooleanField(default=False)
    pooh = models.BooleanField(default=False)


@admin.register(DiaperChange)
class DiaperChangeAdmin(admin.ModelAdmin):
    list_display = ("date", "urine", "pooh")
    ordering = ("-date",)
