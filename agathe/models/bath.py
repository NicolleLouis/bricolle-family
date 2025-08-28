from django.contrib import admin
from django.db import models


class Bath(models.Model):
    date = models.DateTimeField()


@admin.register(Bath)
class BathAdmin(admin.ModelAdmin):
    list_display = ("date",)
    ordering = ("-date",)
