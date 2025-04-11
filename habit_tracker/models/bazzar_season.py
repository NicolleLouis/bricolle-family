from django.contrib import admin
from django.db import models


class BazaarSeason(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    number = models.IntegerField()
    name = models.CharField(
        max_length=12,
    )

    def __str__(self):
        return f"Season {self.number} ({self.name})"


@admin.register(BazaarSeason)
class BazaarSeasonAdmin(admin.ModelAdmin):
    list_display = ('number', 'name')
    search_fields = ["name", "number"]
    ordering = ('created_at',)
