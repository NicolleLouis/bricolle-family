from django.contrib import admin
from django.db import models


class Training(models.Model):
    name = models.CharField(max_length=150)
    training_targets = models.ManyToManyField(
        "sport.TrainingTarget", blank=True, related_name="trainings"
    )
    content = models.TextField(blank=True, help_text="Markdown content")

    def __str__(self):
        return self.name


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("training_targets",)
