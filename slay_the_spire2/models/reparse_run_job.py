from django.contrib import admin
from django.db import models


class ReparseRunJob(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    task_id = models.CharField(max_length=255, blank=True)
    reparsed_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ReparseRunJob #{self.id} ({self.status})"


@admin.register(ReparseRunJob)
class ReparseRunJobAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "reparsed_count", "error_count", "started_at", "finished_at")
    list_filter = ("status",)
    search_fields = ("task_id", "error_message")
    ordering = ("-started_at",)
