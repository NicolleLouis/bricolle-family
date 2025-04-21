from django.contrib import admin
from django.db import models


class BabyBottle(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(help_text="mL")


@admin.register(BabyBottle)
class BabyBottleAdmin(admin.ModelAdmin):
    list_display = ('quantity', 'formatted_created_at')
    ordering = ('-created_at',)

    @admin.display(description='Created At')
    def formatted_created_at(self, obj):
        return obj.created_at.strftime('%d/%m/%Y')
