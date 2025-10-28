from django.contrib import admin
from django.db import models

from capitalism.constants.object_type import ObjectType
from .human import Human


class Object(models.Model):
    owner = models.ForeignKey(Human, on_delete=models.CASCADE, related_name="owned_objects")
    in_sale = models.BooleanField(default=False)
    price = models.FloatField(null=True, blank=True, default=None)
    type = models.CharField(
        max_length=32,
        choices=ObjectType.choices,
        default=ObjectType.BREAD,
    )

    def __str__(self):
        return f"{self.get_type_display()} for {self.owner}"


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "type", "in_sale", "price")
    list_filter = ("type", "in_sale")
    search_fields = ("owner__id", "type")
