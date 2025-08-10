from django.contrib import admin
from django.db import models

from documents.constants.directories import Directories


class Document(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    directory = models.CharField(
        max_length=4,
        choices=Directories.choices,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "directory", "created_at", "updated_at")
    list_filter = ("directory",)
    search_fields = ("title", "content")
    ordering = ("title",)
