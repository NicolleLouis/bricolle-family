from django.contrib import admin
from django.db import models
from django.utils import timezone


class PriceRefreshJob(models.Model):
    class Kind(models.TextChoices):
        LEATHER_JACKET = "leather_jacket", "Leather jacket"
        GATHERING_GEAR = "gathering_gear", "Gathering gear"
        ARTIFACT_SALVAGE = "artifact_salvage", "Artifact salvage"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    kind = models.CharField(max_length=32, choices=Kind.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED, db_index=True)
    task_id = models.CharField(max_length=255, blank=True)
    refreshed_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    context = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-started_at",)

    def __str__(self):
        return f"PriceRefreshJob #{self.id} ({self.kind} - {self.status})"

    def mark_running(self, task_id: str | None):
        self.status = self.Status.RUNNING
        self.task_id = task_id or ""
        self.error_message = ""
        self.save(update_fields=["status", "task_id", "error_message"])

    def mark_success(self, refreshed_count: int):
        self.status = self.Status.SUCCESS
        self.refreshed_count = refreshed_count
        self.error_message = ""
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "refreshed_count", "error_message", "finished_at"])

    def mark_failed(self, error_message: str):
        self.status = self.Status.FAILED
        self.error_message = error_message
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "error_message", "finished_at"])


@admin.register(PriceRefreshJob)
class PriceRefreshJobAdmin(admin.ModelAdmin):
    list_display = ("id", "kind", "status", "refreshed_count", "started_at", "finished_at")
    list_filter = ("kind", "status")
    search_fields = ("task_id", "error_message")
    ordering = ("-started_at",)
