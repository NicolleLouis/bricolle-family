from django.contrib import admin
from django.db import models

from flash_cards.models.question import Question


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        return self.text[:80]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "short_text", "is_correct")
    list_filter = ("is_correct", "question__category")
    search_fields = ("text", "question__text")

    def short_text(self, obj: Answer) -> str:
        return obj.text[:50]
