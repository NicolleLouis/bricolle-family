from django.db.models import OuterRef, Prefetch, Subquery

from albion_online.models import Price, Recipe, RecipeInput


SUMMARY_OBJECT_FIELDS = (
    "id",
    "aodp_id",
    "name",
    "type_id",
    "tier",
    "enchantment",
    "tier_enchantment_notation",
    "equipment_category",
    "crafting_tree",
    "type__resource_return_rate_city",
)

SUMMARY_PRICE_FIELDS = (
    "id",
    "object_id",
    "city",
    "quality",
    "sell_price_min",
    "sell_price_min_date",
    "buy_price_max",
    "buy_price_max_date",
)


def build_latest_price_queryset():
    latest_price_id = Price.objects.filter(
        object_id=OuterRef("object_id"),
        city=OuterRef("city"),
        quality=OuterRef("quality"),
    ).order_by("-sell_price_min_date", "-id").values("id")[:1]
    return Price.objects.filter(id=Subquery(latest_price_id)).only(*SUMMARY_PRICE_FIELDS)


def build_recipe_input_queryset():
    return (
        RecipeInput.objects.select_related("object", "object__type")
        .prefetch_related(Prefetch("object__prices", queryset=build_latest_price_queryset()))
    )


def build_output_recipe_queryset():
    return Recipe.objects.select_related("output", "output__type").prefetch_related(
        Prefetch("inputs", queryset=build_recipe_input_queryset())
    )


def build_market_summary_object_queryset(base_queryset):
    return (
        base_queryset.select_related("type")
        .only(*SUMMARY_OBJECT_FIELDS)
        .prefetch_related(
            Prefetch("prices", queryset=build_latest_price_queryset()),
            Prefetch("output_recipes", queryset=build_output_recipe_queryset()),
        )
    )
