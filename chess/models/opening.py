from django.contrib import admin
from django.db import models


class Opening(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


@admin.register(Opening)
class OpeningAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)
