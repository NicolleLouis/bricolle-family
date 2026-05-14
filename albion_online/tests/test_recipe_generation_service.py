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
        RecipeDefinition.objects.exclude(key="test_mercenary_jacket").update(is_active=False)

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

    def test_refresh_recipes_can_use_unenchanted_input_for_enchanted_output(self):
        output_object = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_LEATHER_MORGANA_GENERATION@1",
            name="Adept's Stalker Jacket",
            type_id=ObjectType.ARMOR,
            tier=4,
            enchantment=1,
            equipment_category=EquipmentCategory.CHEST,
            crafting_tree="leather_chest",
        )
        leather = Object.objects.get(aodp_id="T4_LEATHER_LEVEL1@1")
        leather_folds = Object.objects.get(aodp_id="T4_ARTEFACT_ARMOR_LEATHER_MORGANA")
        recipe_definition = RecipeDefinition.objects.create(
            key="test_stalker_jacket",
            name="Test Stalker Jacket",
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
                    },
                    {
                        "object_filter": {
                            "aodp_id__contains": "ARTEFACT_ARMOR_LEATHER_MORGANA",
                            "type": leather_folds.type_id,
                        },
                        "tier_mode": "same_as_output",
                        "enchantment_mode": "none",
                        "quantity": 1,
                    },
                ],
            },
        )
        RecipeDefinition.objects.exclude(key="test_stalker_jacket").update(is_active=False)

        RecipeGenerationService().refresh_recipes()

        recipe = Recipe.objects.get(output=output_object)
        recipe_inputs = {recipe_input.object: recipe_input.quantity for recipe_input in recipe.inputs.all()}

        assert recipe.definition == recipe_definition
        assert recipe_inputs == {
            leather: 16,
            leather_folds: 1,
        }

    def test_refresh_recipes_supports_artifact_recipe_with_custom_leather_quantity(self):
        output_object = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_LEATHER_FEY_GENERATION@2",
            name="Adept's Mistwalker Jacket",
            type_id=ObjectType.ARMOR,
            tier=4,
            enchantment=2,
            equipment_category=EquipmentCategory.CHEST,
            crafting_tree="leather_chest",
        )
        leather = Object.objects.get(aodp_id="T4_LEATHER_LEVEL2@2")
        griffin_feathers = Object.objects.get(aodp_id="T4_ARTEFACT_ARMOR_LEATHER_FEY")
        recipe_definition = RecipeDefinition.objects.create(
            key="test_mistwalker_jacket",
            name="Test Mistwalker Jacket",
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
                        "quantity": 8,
                    },
                    {
                        "object_filter": {
                            "aodp_id__contains": "ARTEFACT_ARMOR_LEATHER_FEY",
                            "type": griffin_feathers.type_id,
                        },
                        "tier_mode": "same_as_output",
                        "enchantment_mode": "none",
                        "quantity": 1,
                    },
                ],
            },
        )
        RecipeDefinition.objects.exclude(key="test_mistwalker_jacket").update(is_active=False)

        RecipeGenerationService().refresh_recipes()

        recipe = Recipe.objects.get(output=output_object)
        recipe_inputs = {recipe_input.object: recipe_input.quantity for recipe_input in recipe.inputs.all()}

        assert recipe.definition == recipe_definition
        assert recipe_inputs == {
            leather: 8,
            griffin_feathers: 1,
        }
