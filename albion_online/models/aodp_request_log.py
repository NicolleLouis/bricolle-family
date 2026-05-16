from django.contrib import admin
from django.db import models


class AodpRequestLog(models.Model):
    source = models.CharField(max_length=64, db_index=True)
    request_url = models.TextField()
    request_query_string = models.TextField(blank=True)
    response_status_code = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True)
    response_body_raw = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    is_error = models.BooleanField(default=False, db_index=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(fields=("created_at",)),
            models.Index(fields=("source", "created_at")),
            models.Index(fields=("is_error", "created_at")),
        ]

    def __str__(self):
        if self.request_url:
            return f"{self.source} - {self.request_url}"
        return self.source


@admin.register(AodpRequestLog)
class AodpRequestLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "source",
        "response_status_code",
        "is_error",
        "duration_ms",
    )
    list_filter = ("source", "is_error", "response_status_code", "created_at")
    search_fields = (
        "source",
        "request_url",
        "request_query_string",
        "response_body_raw",
        "error_message",
    )
    ordering = ("-created_at", "-id")
