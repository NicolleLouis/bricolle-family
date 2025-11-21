from django.contrib import admin
from django.db import models

from flash_cards.models.category import Category


class ThemePreset(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_exclusion = models.BooleanField(default=False)
    categories = models.ManyToManyField(
        Category, related_name="theme_presets", blank=True
    )

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


@admin.register(ThemePreset)
class ThemePresetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_exclusion", "category_list")
    list_filter = ("is_exclusion", "categories")
    search_fields = ("name",)
    filter_horizontal = ("categories",)

    def category_list(self, obj: ThemePreset) -> str:
        return ", ".join(obj.categories.values_list("name", flat=True))
