from django.contrib import admin
from django.db import models


class AspirinIntake(models.Model):
    date = models.DateTimeField()


@admin.register(AspirinIntake)
class AspirinIntakeAdmin(admin.ModelAdmin):
    list_display = ("date",)
    ordering = ("-date",)
