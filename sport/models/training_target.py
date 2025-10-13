from django.contrib import admin
from django.db import models


class TrainingTarget(models.Model):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


@admin.register(TrainingTarget)
class TrainingTargetAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
