from django.contrib import admin
from django.core.validators import RegexValidator
from django.db import models


class Season(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    number = models.IntegerField(unique=True)
    name = models.CharField(
        max_length=100,
        unique=True,
    )
    version = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\d+\.\d+\.\d+$',
                message="Version must be of format X.Y.Z (typically, 1.0.0)."
            )
        ]
    )


    def __str__(self):
        return f"Season {self.number} ({self.name})"


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('number', 'name')
    search_fields = ["name", "number"]
    ordering = ('created_at',)