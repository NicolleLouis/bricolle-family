from django.contrib import admin
from django.db import models


class Game(models.TextChoices):
    BACK_TO_THE_DAWN = "bttd", "Back to the Dawn"


class Document(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    game = models.CharField(
        max_length=50,
        choices=Game.choices,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "game", "created_at", "updated_at")
    list_filter = ("game",)
    search_fields = ("title", "content")
    ordering = ("title",)
