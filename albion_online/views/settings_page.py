from django.contrib import messages
from django.shortcuts import redirect, render

from albion_online.models import RecipeDefinition
from albion_online.services.recipe_generation import RecipeGenerationService


def settings_page(request):
    if request.method == "POST":
        try:
            generated_recipes = RecipeGenerationService().refresh_recipes()
        except Exception as exception:
            messages.error(request, f"Recipe regeneration failed: {exception}")
        else:
            messages.success(
                request,
                f"{len(generated_recipes)} recipes regenerated from active definitions.",
            )
        return redirect("albion_online:settings")

    return render(
        request,
        "albion_online/settings.html",
        {
            "recipe_definitions": RecipeDefinition.objects.order_by("key"),
        },
    )
