from django.contrib import admin
from django.db import models


class VitaminIntake(models.Model):
    date = models.DateTimeField()


@admin.register(VitaminIntake)
class VitaminIntakeAdmin(admin.ModelAdmin):
    list_display = ("date",)
    ordering = ("-date",)
