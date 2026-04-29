import pytest

from albion_online.models import Object, Recipe, RecipeDefinition
from albion_online.constants.equipment_category import EquipmentCategory
from albion_online.constants.object_type import ObjectType
from albion_online.services.recipe_generation import RecipeGenerationService


@pytest.mark.django_db
class TestRecipeGenerationService:
    def test_refresh_recipes_deletes_and_rebuilds_existing_recipes(self):
        output_object = Object.objects.create(
            aodp_id="TEST_RECIPE_OUTPUT_GENERATION",
            name="Test Jacket",
            type_id=ObjectType.ARMOR,
            tier=4,
            enchantment=0,
            equipment_category=EquipmentCategory.CHEST,
            crafting_tree="leather_chest",
        )
        leather = Object.objects.get(aodp_id="T4_LEATHER")
        recipe_definition = RecipeDefinition.objects.create(
            key="test_mercenary_jacket",
            name="Test Mercenary Jacket",
            config={
                "output_filter": {
                    "aodp_id": output_object.aodp_id,
                },
                "output_quantity": 1,
                "inputs": [
                    {
                        "object_filter": {
                            "type": leather.type_id,
                        },
                        "tier_mode": "same_as_output",
                        "enchantment_mode": "same_as_output",
                        "quantity": 16,
                    }
                ],
            },
        )
        RecipeDefinition.objects.filter(
            key__in=["mercenary_jacket", "hunter_jacket", "assassin_jacket"],
        ).update(is_active=False)

        first_created_recipes = RecipeGenerationService().refresh_recipes()

        recipe = Recipe.objects.get(output=output_object)
        recipe_input = recipe.inputs.get()
        recipe_input.quantity = 1
        recipe_input.save(update_fields=["quantity"])

        second_created_recipes = RecipeGenerationService().refresh_recipes()

        refreshed_recipe = Recipe.objects.get(output=output_object)
        refreshed_recipe_input = refreshed_recipe.inputs.get()

        assert len(first_created_recipes) == 1
        assert len(second_created_recipes) == 1
        assert refreshed_recipe.definition == recipe_definition
        assert refreshed_recipe.output == output_object
        assert refreshed_recipe_input.object == leather
        assert refreshed_recipe_input.quantity == 16
