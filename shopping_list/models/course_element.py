from django.contrib import admin
from django.db import models


class CourseElement(models.Model):
    course = models.ForeignKey('shopping_list.Course', related_name='course_elements', on_delete=models.CASCADE)
    ingredient = models.ForeignKey('shopping_list.Ingredient', on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.ingredient.name}: {self.quantity}"


class CourseElementAdmin(admin.ModelAdmin):
    list_display = ('course', 'ingredient', 'quantity')
    list_filter = ('course__name',)
    search_fields = ['ingredient__name', 'course__name']
    ordering = ('course', 'ingredient')
