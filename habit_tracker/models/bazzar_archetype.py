from django.contrib import admin
from django.db import models

from habit_tracker.constants.bazaar.character import Character


class BazaarArchetype(models.Model):
    name = models.CharField(max_length=18)
    character = models.CharField(
        max_length=9,
        choices=Character.choices,
        default=Character.VANESSA
    )
    is_meta_viable = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


@admin.register(BazaarArchetype)
class BazaarArchetypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'character')
    list_filter = ('character', 'is_meta_viable')
    search_fields = ["name"]
    actions = ["set_meta_viable", "set_meta_not_viable"]

    @admin.action(description="Meta viable")
    def set_meta_viable(self, request, queryset):
        queryset.update(is_meta_viable=True)

    @admin.action(description="Not meta viable")
    def set_meta_not_viable(self, request, queryset):
        queryset.update(is_meta_viable=False)
