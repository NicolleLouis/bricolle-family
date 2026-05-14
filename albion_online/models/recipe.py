from django.contrib import admin
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from albion_online.constants.city import City
from albion_online.models.object import Object


class RecipeDefinition(models.Model):
    key = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    config = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ("key",)

    def __str__(self):
        return self.name


@admin.register(RecipeDefinition)
class RecipeDefinitionAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("key", "name")


class Recipe(models.Model):
    definition = models.ForeignKey(
        RecipeDefinition,
        on_delete=models.CASCADE,
        related_name="recipes",
        null=True,
        blank=True,
    )
    output = models.ForeignKey(
        Object,
        on_delete=models.CASCADE,
        related_name="output_recipes",
    )
    output_quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ("output__crafting_tree", "output__tier", "output__enchantment", "output__aodp_id")
        constraints = [
            models.UniqueConstraint(fields=("output",), name="albion_unique_recipe_output"),
        ]

    def __str__(self):
        notation = self.output.tier_enchantment_notation or "no tier"
        return f"{self.output.name or self.output.aodp_id} {notation}"


class RecipeInput(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="inputs",
    )
    object = models.ForeignKey(
        Object,
        on_delete=models.CASCADE,
        related_name="recipe_inputs",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ("recipe_id", "object__type", "object__aodp_id")
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "object"),
                name="albion_unique_recipe_input_object",
            ),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.object.name or self.object.aodp_id}"


class CraftProfitabilityDone(models.Model):
    object = models.ForeignKey(
        Object,
        on_delete=models.CASCADE,
        related_name="craft_profitability_done_records",
    )
    city = models.CharField(max_length=16, choices=City.choices, db_index=True)
    completed_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ("-completed_at", "city", "object")
        constraints = [
            models.UniqueConstraint(
                fields=("object", "city"),
                name="albion_unique_gathering_gear_profitability_done_craft",
            ),
        ]

    def __str__(self):
        return f"{self.object} - {self.city} - {self.completed_at.isoformat()}"


@admin.register(CraftProfitabilityDone)
class CraftProfitabilityDoneAdmin(admin.ModelAdmin):
    list_display = ("object", "city", "completed_at")
    list_filter = ("city", "completed_at")
    search_fields = ("object__aodp_id", "object__name")
    autocomplete_fields = ("object",)


class RecipeInputInline(admin.TabularInline):
    model = RecipeInput
    autocomplete_fields = ("object",)
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("definition", "output", "output_quantity", "output_notation")
    list_filter = (
        "definition",
        "output__crafting_tree",
        "output__tier_enchantment_notation",
        "output__tier",
        "output__enchantment",
    )
    search_fields = ("output__aodp_id", "output__name")
    autocomplete_fields = ("output",)
    inlines = (RecipeInputInline,)
    ordering = ("output__crafting_tree", "output__tier", "output__enchantment", "output__aodp_id")

    @admin.display(description="Tier")
    def output_notation(self, recipe):
        return recipe.output.tier_enchantment_notation


@admin.register(RecipeInput)
class RecipeInputAdmin(admin.ModelAdmin):
    list_display = ("recipe", "object", "quantity", "input_notation")
    list_filter = (
        "object__type",
        "object__crafting_tree",
        "object__tier_enchantment_notation",
    )
    search_fields = ("recipe__output__aodp_id", "recipe__output__name", "object__aodp_id", "object__name")
    autocomplete_fields = ("recipe", "object")

    @admin.display(description="Tier")
    def input_notation(self, recipe_input):
        return recipe_input.object.tier_enchantment_notation
