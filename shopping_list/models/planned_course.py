from django.contrib import admin
from django.db import models


class PlannedCourse(models.Model):
    course = models.ForeignKey('shopping_list.Course', related_name='wanted_courses', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} {self.course.name}"


class PlannedCourseAdmin(admin.ModelAdmin):
    list_display = ('course', 'quantity')
    list_filter = ('course__name',)
    search_fields = ['course__name']
    ordering = ('course',)
