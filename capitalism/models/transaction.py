from django.contrib import admin
from django.db import models

from capitalism.constants.object_type import ObjectType


class Transaction(models.Model):
    object_type = models.CharField(
        max_length=32,
        choices=ObjectType.choices,
    )
    price = models.FloatField()

    def __str__(self):
        return f"{self.get_object_type_display()} sold for {self.price}"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "object_type", "price")
    list_filter = ("object_type",)
