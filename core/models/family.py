from django.db import models
from django.contrib import admin


class Family(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ["name"]
    ordering = ('name',)
