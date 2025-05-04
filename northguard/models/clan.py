from django.contrib import admin
from django.db import models

from northguard.constants.clan_name import ClanName


class Clan(models.Model):
    name = models.CharField(
        max_length=8,
        choices=ClanName.choices,
        default=ClanName.STAG,
        unique=True
    )
    image = models.ImageField(upload_to='northguard/clan_images/', null=True, blank=True)

    def __str__(self):
        return self.get_name_display()


@admin.register(Clan)
class ClanAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
