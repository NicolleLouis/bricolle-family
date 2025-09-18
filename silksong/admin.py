from django.contrib import admin

from silksong.models import GameSession


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ("type", "created_at", "boss", "duration", "victory")
    list_filter = ("type", "victory", "boss")
    ordering = ("-created_at",)
