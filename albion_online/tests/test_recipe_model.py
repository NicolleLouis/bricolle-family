import pytest
from django.core.exceptions import ValidationError

from albion_online.models import Object, Recipe, RecipeInput


@pytest.mark.django_db
class TestRecipeModel:
    def test_create_recipe_with_input_and_output_objects(self):
        leather = Object.objects.get(aodp_id="T5_LEATHER_LEVEL1@1")
        mercenary_jacket = Object.objects.get(aodp_id="T5_ARMOR_LEATHER_SET1@1")

        recipe = Recipe.objects.create(output=mercenary_jacket, output_quantity=1)
        recipe_input = RecipeInput.objects.create(
            recipe=recipe,
            object=leather,
            quantity=16,
        )

        assert recipe.output == mercenary_jacket
        assert recipe.output.tier_enchantment_notation == "5.1"
        assert recipe.output_quantity == 1
        assert recipe_input.object == leather
        assert recipe_input.object.tier_enchantment_notation == "5.1"
        assert recipe_input.quantity == 16

    def test_object_save_records_tier_enchantment_notation(self):
        albion_object = Object.objects.create(
            aodp_id="TEST_T5_1_OBJECT",
            name="Test Object",
            type_id="ARMOR",
            tier=5,
            enchantment=1,
            equipment_category="CHEST",
            crafting_tree="leather_chest",
        )

        assert albion_object.tier_enchantment_notation == "5.1"

    def test_object_display_name_strips_tier_prefix_and_appends_notation(self):
        albion_object = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_LEATHER_SET1@2",
            name="Adept's Mercenary Jacket",
            type_id="ARMOR",
            tier=4,
            enchantment=2,
            equipment_category="CHEST",
            crafting_tree="leather_chest",
        )

        assert albion_object.display_name == "Mercenary Jacket 4.2"

    def test_recipe_input_quantity_must_be_positive(self):
        leather = Object.objects.get(aodp_id="T5_LEATHER_LEVEL1@1")
        mercenary_jacket = Object.objects.get(aodp_id="T5_ARMOR_LEATHER_SET1@1")
        recipe = Recipe.objects.create(output=mercenary_jacket, output_quantity=1)
        recipe_input = RecipeInput(recipe=recipe, object=leather, quantity=0)

        with pytest.raises(ValidationError):
            recipe_input.full_clean()
