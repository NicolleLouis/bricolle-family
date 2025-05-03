from django.contrib import admin
from django.db import models
from django.core.validators import MinValueValidator

from northguard.models import BuildOrder, BuildOrderMilestone


class BuildOrderStep(models.Model):
    build_order = models.ForeignKey(
        BuildOrder,
        on_delete=models.CASCADE,
        related_name="steps",
    )
    order = models.IntegerField(
        null=False,
        validators=[MinValueValidator(0)]
    )
    milestone = models.ForeignKey(
        BuildOrderMilestone,
        on_delete=models.PROTECT,
    )

    class Meta:
        unique_together = ('build_order', 'order')


@admin.register(BuildOrderStep)
class BuildOrderStepAdmin(admin.ModelAdmin):
    list_display = ('build_order', 'milestone', 'order')
    ordering = ('order',)
    list_filter = ('build_order', 'milestone',)
