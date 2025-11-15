from django.contrib import admin
from django.db import models

from flash_cards.models.category import Category


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    explanation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_answer = models.DateTimeField(null=True, blank=True)
    answer_number = models.PositiveIntegerField(default=0)
    last_answer_result = models.BooleanField(default=False)
    positive_answer_number = models.PositiveIntegerField(default=0)
    negative_answer_number = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.text[:80]

    @property
    def is_valid(self) -> bool:
        positive = getattr(self, "positive_answers", None)
        negative = getattr(self, "negative_answers", None)
        if positive is not None and negative is not None:
            return positive > 0 and negative > 0
        return (
            self.answers.filter(is_correct=True).exists()
            and self.answers.filter(is_correct=False).exists()
        )

    @property
    def error_rate(self) -> float:
        if self.answer_number == 0:
            return 0.0
        return self.negative_answer_number / self.answer_number


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "category",
        "short_text",
        "answer_number",
        "positive_answer_number",
        "negative_answer_number",
        "last_answer_result",
    )
    list_filter = ("category", "last_answer_result")
    search_fields = ("text",)

    def short_text(self, obj: Question) -> str:
        return obj.text[:50]
