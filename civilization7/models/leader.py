from django.contrib import admin
from django.db import models


class Leader(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
