from django.contrib import admin
from django.db import models

from the_bazaar.constants.character import Character


class Fight(models.Model):
    run = models.ForeignKey(
        'the_bazaar.Run',
        on_delete=models.CASCADE,
        related_name='fights'
    )
    opponent_character = models.CharField(
        max_length=9,
        choices=Character.choices
    )
    day_number = models.PositiveIntegerField()
    opponent_archetype = models.ForeignKey(
        'the_bazaar.Archetype',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    comment = models.TextField(blank=True)
    is_victory = models.BooleanField(default=False)

    class Meta:
        unique_together = ('run', 'day_number')
        ordering = ['day_number']

    def __str__(self):
        return f"Day {self.day_number} vs {self.opponent_character}"


@admin.register(Fight)
class FightAdmin(admin.ModelAdmin):
    list_display = ('run', 'day_number', 'opponent_character', 'opponent_archetype', 'is_victory')
    list_filter = ('opponent_character', 'opponent_archetype', 'is_victory')
    search_fields = ('run__id',)
