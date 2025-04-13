from django.contrib import admin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class CourseHistory(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey('shopping_list.Course', on_delete=models.PROTECT)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.course.name} ({self.rating})"


@admin.register(CourseHistory)
class CourseHistoryAdmin(admin.ModelAdmin):
    list_display = ('course', 'rating', 'formatted_created_at')
    search_fields = ['course__name',]
    list_filter = ['course', 'rating']
    ordering = ('-created_at',)

    @admin.display(description='Created At')
    def formatted_created_at(self, obj):
        return obj.created_at.strftime('%d/%m/%Y')
