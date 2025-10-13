from django.contrib import admin
from django.db import models


class Session(models.Model):
    date = models.DateField()
    training = models.ForeignKey(
        "sport.Training", on_delete=models.CASCADE, related_name="sessions"
    )

    def __str__(self):
        return f"{self.training} - {self.date}"


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("date", "training")
    list_filter = ("date", "training")
    search_fields = ("training__name",)
