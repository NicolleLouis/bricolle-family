from django.contrib import admin
from django.db import models


class RunSummaryCard(models.Model):
    run_summary = models.ForeignKey(
        "slay_the_spire2.RunSummary",
        on_delete=models.CASCADE,
        related_name="deck_entries",
    )
    card = models.ForeignKey(
        "slay_the_spire2.Card",
        on_delete=models.CASCADE,
        related_name="run_summary_entries",
    )
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("run_summary", "card"),
                name="sts_unique_run_summary_card",
            )
        ]
        indexes = [
            models.Index(fields=("run_summary",), name="sts_rsc_run_summary_idx"),
            models.Index(fields=("card",), name="sts_rsc_card_idx"),
        ]

    def __str__(self):
        return f"{self.card.name} x{self.quantity} ({self.run_summary_id})"


@admin.register(RunSummaryCard)
class RunSummaryCardAdmin(admin.ModelAdmin):
    list_display = ("id", "run_summary", "card", "quantity")
    list_filter = ("card",)
    search_fields = ("run_summary__run_file__original_file_name", "card__name")
    ordering = ("-id",)
