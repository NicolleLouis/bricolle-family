from django.contrib import admin
from django.contrib import messages
from django.db import models


class RunSummary(models.Model):
    run_file = models.OneToOneField(
        "slay_the_spire2.RunFile",
        on_delete=models.CASCADE,
        related_name="summary",
    )
    win = models.BooleanField()
    abandonned = models.BooleanField()
    character = models.ForeignKey(
        "slay_the_spire2.Character",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="run_summaries",
    )
    start_time = models.IntegerField(null=True, blank=True)
    ascension = models.IntegerField()
    killed_by = models.ForeignKey(
        "slay_the_spire2.Encounter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="killed_run_summaries",
    )
    relics = models.ManyToManyField(
        "slay_the_spire2.Relic",
        blank=True,
        related_name="run_summaries",
    )
    cards = models.ManyToManyField(
        "slay_the_spire2.Card",
        through="slay_the_spire2.RunSummaryCard",
        blank=True,
        related_name="run_summaries",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Summary for {self.run_file.original_file_name}"


@admin.register(RunSummary)
class RunSummaryAdmin(admin.ModelAdmin):
    list_display = ("id", "run_file", "win", "abandonned", "character", "start_time", "ascension", "killed_by")
    list_filter = ("win", "abandonned", "ascension", "character", "killed_by")
    search_fields = ("run_file__original_file_name", "killed_by__name", "character__name")
    ordering = ("-updated_at",)
    actions = ("reparse_selected_run_files",)

    @admin.action(description="Re-parser les fichiers des runs selectionnees")
    def reparse_selected_run_files(self, request, queryset):
        from slay_the_spire2.services.reparse_run_files import ReparseRunFilesService

        reparse_service = ReparseRunFilesService()
        reparsed_count = 0
        error_count = 0

        for run_summary in queryset.select_related("run_file"):
            try:
                reparse_service.reparse_one(run_summary.run_file)
                reparsed_count += 1
            except ValueError:
                error_count += 1

        if reparsed_count:
            self.message_user(
                request,
                f"{reparsed_count} fichier(s) re-parse(s) avec succes.",
                level=messages.SUCCESS,
            )

        if error_count:
            self.message_user(
                request,
                f"{error_count} fichier(s) en erreur pendant le re-parse.",
                level=messages.ERROR,
            )
