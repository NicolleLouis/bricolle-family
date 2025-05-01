from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from the_bazaar.constants.character import Character
from the_bazaar.constants.result import Result


class Run(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    character = models.CharField(
        max_length=9,
        choices=Character.choices,
        default=Character.VANESSA
    )
    archetype = models.ForeignKey(
        'the_bazaar.Archetype',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    season = models.ForeignKey(
        'the_bazaar.Season',
        on_delete=models.PROTECT,
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

    def save(self, *args, **kwargs):
        self.set_victory_type()
        self.set_season()
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.archetype and self.archetype.character != self.character:
            raise ValidationError(
                {"archetype": "Archetype is not valid for this character"}
            )

    def __str__(self):
        display = f"{self.character}: {self.win_number} wins"
        if self.archetype is not None:
            display += f" ({self.archetype.name})"
        return display

    def set_victory_type(self):
        if self.win_number < 4:
            self.result = Result.LOSS
        elif self.win_number < 7:
            self.result = Result.BRONZE_WIN
        elif self.win_number < 10:
            self.result = Result.SILVER_WIN
        else:
            self.result = Result.GOLD_WIN

    def set_season(self):
        if self.season is None:
            from the_bazaar.models import Season
            newest_season = Season.objects.order_by('-created_at').first()
            self.season = newest_season

    @property
    def elo_change(self):
        match self.result:
            case Result.LOSS:
                return -1
            case Result.BRONZE_WIN:
                return 0
            case Result.SILVER_WIN:
                return 1
            case Result.GOLD_WIN:
                return 2


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ('character', 'archetype', 'result', 'formatted_created_at')
    list_filter = ('character', 'archetype', 'result')
    search_fields = ["character", "archetype__name"]
    readonly_fields = ('result',)
    ordering = ('-created_at',)

    @admin.display(description='Created At')
    def formatted_created_at(self, obj):
        return obj.created_at.strftime('%d/%m/%Y')