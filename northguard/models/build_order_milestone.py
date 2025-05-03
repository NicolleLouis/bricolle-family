from django.contrib import admin
from django.db import models

from northguard.constants.build_order_milestone_name import BuildOrderMilestoneName
from northguard.constants.build_order_milestone_type import BuildOrderMilestoneType


class BuildOrderMilestone(models.Model):
    name = models.CharField(
        max_length=10,
        choices=BuildOrderMilestoneName.choices,
        default=BuildOrderMilestoneName.SCOUT,
        unique=True
    )
    type = models.CharField(
        max_length=10,
        choices=BuildOrderMilestoneType.choices,
        default=BuildOrderMilestoneType.BUILDING,
        unique=True
    )
    image = models.ImageField(upload_to='northguard/milestone_image/', null=True, blank=True)


@admin.register(BuildOrderMilestone)
class BuildOrderMilestoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'type',)
    ordering = ('name',)
