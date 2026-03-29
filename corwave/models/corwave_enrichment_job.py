from django.contrib import admin
from django.db import models


class CorwaveEnrichmentJob(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )
    input_file = models.FileField(upload_to="corwave/input/")
    input_file_name = models.CharField(max_length=255)
    output_file = models.FileField(upload_to="corwave/output/", blank=True, null=True)
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Corwave job #{self.id} ({self.status})"


@admin.register(CorwaveEnrichmentJob)
class CorwaveEnrichmentJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "input_file_name",
        "total_rows",
        "processed_rows",
        "created_at",
        "finished_at",
    )
    list_filter = ("status", "created_at", "finished_at")
    search_fields = ("id", "input_file_name", "error_message")
    readonly_fields = ("created_at", "started_at", "finished_at")
