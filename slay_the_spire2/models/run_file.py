import os

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models, transaction

from slay_the_spire2.services.run_file_parser import RunFileParserService
from slay_the_spire2.services.run_summary_builder import RunSummaryBuilderService


class RunFile(models.Model):
    file = models.FileField(upload_to="slay_the_spire2/run_files/")
    original_file_name = models.CharField(max_length=255, blank=True)
    parsed_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.file:
                self.original_file_name = os.path.basename(self.file.name)
                try:
                    self.parsed_payload = RunFileParserService().parse_uploaded_file(self.file)
                except ValueError as error:
                    raise ValidationError({"file": str(error)}) from error

            super().save(*args, **kwargs)

            if self.file:
                try:
                    RunSummaryBuilderService().upsert_from_run_file(self)
                except ValueError as error:
                    raise ValidationError({"file": str(error)}) from error

    def __str__(self):
        return self.original_file_name


@admin.register(RunFile)
class RunFileAdmin(admin.ModelAdmin):
    list_display = ("id", "original_file_name", "file", "created_at")
    search_fields = ("original_file_name",)
    ordering = ("-created_at",)
