from django.db import models
from django.contrib.auth.models import User

from django.contrib import admin
from core.models.family import Family


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    family = models.ForeignKey(Family, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'family')
    list_filter = ('family',)
    search_fields = ["user__username"]
    ordering = ('user__username',)
