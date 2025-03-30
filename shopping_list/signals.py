from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PlannedCourse, ShoppingListItem, Ingredient

@receiver(post_save, sender=PlannedCourse)
def enrich_shopping_list(sender, instance, created, **kwargs):
    if not created:
        return

    course_elements = instance.course.course_elements.all()

    for course_element in course_elements:
        ingredient = course_element.ingredient
        quantity = course_element.quantity

        planned_ingredient, ingredient_created = ShoppingListItem.objects.get_or_create(
            ingredient=ingredient,
            defaults={'quantity': quantity}
        )
        if not ingredient_created:
            planned_ingredient.quantity += quantity
            planned_ingredient.save()
