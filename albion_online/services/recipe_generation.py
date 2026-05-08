from django.db import transaction

from albion_online.models import Object, Recipe, RecipeDefinition, RecipeInput


class RecipeGenerationService:
    def refresh_recipes(self) -> list[Recipe]:
        created_recipes = []
        for recipe_definition in RecipeDefinition.objects.filter(is_active=True).order_by("key"):
            created_recipes.extend(self._refresh_recipe_definition(recipe_definition))
        return created_recipes

    def _refresh_recipe_definition(self, recipe_definition: RecipeDefinition) -> list[Recipe]:
        output_objects = list(self._build_output_objects(recipe_definition))

        with transaction.atomic():
            recipe_definition.recipes.all().delete()
            if not output_objects:
                return []
            created_recipes = []
            for output_object in output_objects:
                created_recipe = Recipe.objects.create(
                    definition=recipe_definition,
                    output=output_object,
                    output_quantity=self._build_output_quantity(recipe_definition),
                )
                recipe_inputs = [
                    RecipeInput(
                        recipe=created_recipe,
                        object=input_object,
                        quantity=input_quantity,
                    )
                    for input_object, input_quantity in self._build_recipe_inputs(recipe_definition, output_object)
                ]
                RecipeInput.objects.bulk_create(recipe_inputs)
                created_recipes.append(created_recipe)
            return created_recipes

    def _build_output_objects(self, recipe_definition: RecipeDefinition):
        output_filter = recipe_definition.config.get("output_filter", {})
        return Object.objects.filter(**output_filter).order_by("aodp_id")

    def _build_output_quantity(self, recipe_definition: RecipeDefinition) -> int:
        return int(recipe_definition.config.get("output_quantity", 1))

    def _build_recipe_inputs(self, recipe_definition: RecipeDefinition, output_object: Object):
        recipe_input_definitions = recipe_definition.config.get("inputs", [])
        built_inputs = []
        for recipe_input_definition in recipe_input_definitions:
            built_inputs.append(
                (
                    self._build_input_object(recipe_input_definition, output_object),
                    int(recipe_input_definition.get("quantity", 1)),
                )
            )
        return built_inputs

    def _build_input_object(self, recipe_input_definition, output_object: Object) -> Object:
        input_filter = dict(recipe_input_definition.get("object_filter", {}))
        if recipe_input_definition.get("tier_mode") == "same_as_output":
            input_filter["tier"] = output_object.tier
        if recipe_input_definition.get("enchantment_mode") == "same_as_output":
            input_filter["enchantment"] = output_object.enchantment
        if recipe_input_definition.get("enchantment_mode") == "none":
            input_filter["enchantment"] = 0

        matching_objects = list(Object.objects.filter(**input_filter).order_by("aodp_id"))
        if not matching_objects:
            raise ValueError(
                f"Unable to build recipe input for output={output_object.aodp_id} with filter={input_filter}"
            )
        if len(matching_objects) > 1:
            raise ValueError(
                f"Recipe input filter matched multiple objects for output={output_object.aodp_id}: {input_filter}"
            )
        return matching_objects[0]
