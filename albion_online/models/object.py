import re

from django.contrib import admin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from albion_online.constants.city import City
from albion_online.constants.crafting_tree import CraftingTree
from albion_online.constants.equipment_category import EquipmentCategory


class ObjectTypeGroup(models.Model):
    code = models.SlugField(max_length=32, primary_key=True)
    name = models.CharField(max_length=255)
    resource_return_rate_city = models.CharField(max_length=16, choices=City.choices, null=True, blank=True, db_index=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return self.name


@admin.register(ObjectTypeGroup)
class ObjectTypeGroupAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "resource_return_rate_city")
    list_filter = ("resource_return_rate_city",)
    search_fields = ("code", "name")


class Object(models.Model):
    _leading_tier_name_pattern = re.compile(r"^[A-Za-zÀ-ÿ' -]+\'s\s+")

    aodp_id = models.CharField(max_length=120, unique=True)
    name = models.CharField(max_length=255, blank=True)
    type = models.ForeignKey(
        ObjectTypeGroup,
        on_delete=models.PROTECT,
        to_field="code",
        db_column="type",
        related_name="typed_objects",
    )
    tier = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        db_index=True,
    )
    enchantment = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        db_index=True,
    )
    tier_enchantment_notation = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        db_index=True,
    )
    equipment_category = models.CharField(
        max_length=16,
        choices=EquipmentCategory.choices,
        null=True,
        blank=True,
        db_index=True,
    )
    crafting_tree = models.CharField(
        max_length=64,
        choices=CraftingTree.choices,
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        ordering = (
            "crafting_tree",
            "equipment_category",
            "type",
            "tier",
            "enchantment",
            "aodp_id",
        )

    def save(self, *args, **kwargs):
        self.tier_enchantment_notation = self.build_tier_enchantment_notation()
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = set(update_fields)
            update_fields.add("tier_enchantment_notation")
            kwargs["update_fields"] = list(update_fields)
        super().save(*args, **kwargs)

    def build_tier_enchantment_notation(self):
        if self.tier is None:
            return None
        return f"{self.tier}.{self.enchantment}"

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.aodp_id})"
        return self.aodp_id

    @property
    def type_code(self):
        return self.type_id

    @property
    def display_name(self):
        if not self.name:
            return self.aodp_id

        normalized_name = self._leading_tier_name_pattern.sub("", self.name).strip()
        if self.tier_enchantment_notation is None:
            return normalized_name
        return f"{normalized_name} {self.tier_enchantment_notation}"


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = (
        "aodp_id",
        "name",
        "type",
        "equipment_category",
        "crafting_tree",
        "tier_enchantment_notation",
        "tier",
        "enchantment",
    )
    list_filter = (
        "equipment_category",
        "crafting_tree",
        "tier_enchantment_notation",
        "type",
        "tier",
        "enchantment",
    )
    search_fields = ("aodp_id", "name")
    ordering = (
        "crafting_tree",
        "equipment_category",
        "type",
        "tier",
        "enchantment",
        "aodp_id",
    )
