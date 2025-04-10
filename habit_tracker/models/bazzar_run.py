from django.contrib import admin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from habit_tracker.constants.bazaar.archetype import Archetype
from habit_tracker.constants.bazaar.character import Character
from habit_tracker.constants.bazaar.result import Result


class BazaarRun(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    character = models.CharField(
        max_length=9,
        choices=Character.choices,
        default=Character.VANESSA
    )
    archetype = models.CharField(
        max_length=17,
        choices=Archetype.choices,
        null=True,
        blank=True,
    )
    win_number = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    notes = models.TextField(null=True, blank=True)
    result = models.CharField(
        max_length=10,
        choices=Result.choices,
        blank=True
    )

    class Meta:
        permissions = [
            ("bazaar_access", "Can access bazaar pages")
        ]

    def save(self, *args, **kwargs):
        self.set_victory_type()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.character}: {self.win_number} wins ({self.archetype})"

    def set_victory_type(self):
        if self.win_number < 4:
            self.result = Result.LOSS
        elif self.win_number < 7:
            self.result = Result.BRONZE_WIN
        elif self.win_number < 10:
            self.result = Result.SILVER_WIN
        else:
            self.result = Result.GOLD_WIN


@admin.register(BazaarRun)
class BazaarRunAdmin(admin.ModelAdmin):
    list_display = ('character', 'archetype', 'result', 'formatted_created_at')
    list_filter = ('character', 'archetype', 'result')
    search_fields = ["character", "archetype"]
    ordering = ('created_at',)
    readonly_fields = ('result', )
    ordering = ('-created_at', )

    @admin.display(description='Created At')
    def formatted_created_at(self, obj):
        return obj.created_at.strftime('%d/%m/%Y')
