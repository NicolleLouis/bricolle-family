from django.contrib import admin
from django.db import models
from northguard.models.clan import Clan


class BuildOrder(models.Model):
    name = models.CharField(
        max_length=8,
        null=True,
        blank=True,
    )
    state_of_the_art = models.BooleanField(
        default=False,
    )
    clan = models.ForeignKey(
        Clan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="build_orders",
    )

    def __str__(self):
        return f"{self.name} ({self.clan.get_name_display()})"


@admin.register(BuildOrder)
class BuildOrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'clan', 'state_of_the_art')
    ordering = ('name',)
