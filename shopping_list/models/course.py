from django.contrib import admin
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']
    ordering = ('name',)
