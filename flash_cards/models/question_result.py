from django.conf import settings
from django.contrib import admin
from django.db import models

from flash_cards.models.question import Question


class QuestionResult(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="question_results",
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="results"
    )
    last_answer = models.DateTimeField(null=True, blank=True)
    answer_number = models.PositiveIntegerField(default=0)
    last_answer_result = models.BooleanField(default=False)
    positive_answer_number = models.PositiveIntegerField(default=0)
    negative_answer_number = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("user", "question")
        unique_together = ("user", "question")

    def __str__(self) -> str:
        return f"{self.user} - {self.question}"


@admin.register(QuestionResult)
class QuestionResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "question",
        "answer_number",
        "positive_answer_number",
        "negative_answer_number",
        "last_answer_result",
        "last_answer",
    )
    list_filter = ("last_answer_result", "user")
    search_fields = ("question__text", "user__username", "user__email")
