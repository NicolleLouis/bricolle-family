import json
from decimal import Decimal

from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from shopping_list.models import ShoppingListItem, Ingredient


class PlannedIngredientController:
    @staticmethod
    def index(request):
        shopping_list = ShoppingListItem.objects.all()

        return render(
            request,
            "shopping_list/shopping_list.html",
            {"shopping_list": shopping_list}
        )

    @staticmethod
    def delete(request):
        try:
            data = json.loads(request.body)
            planned_ingredient_id = data.get('planned_ingredient_id')
            if not planned_ingredient_id:
                return JsonResponse({"status": "error", "message": "Missing planned_ingredient_id."}, status=400)

            planned_course = get_object_or_404(ShoppingListItem, id=planned_ingredient_id)
            planned_course.delete()

            return JsonResponse({"status": "success", "message": "Course removed."})

        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON.")

    @staticmethod
    def add_api(request):
        ingredient_id = request.POST.get("ingredient_id")
        quantity = Decimal(request.POST.get("ingredient_quantity"))
        if not ingredient_id:
            return JsonResponse({"status": "error", "message": "Missing ingredient_id."}, status=400)

        ingredient = get_object_or_404(Ingredient, id=ingredient_id)

        planned_ingredient, created = ShoppingListItem.objects.get_or_create(
            ingredient=ingredient,
            defaults={'quantity': quantity}
        )
        if not created:
            planned_ingredient.quantity += quantity
            planned_ingredient.save()

        return redirect('shopping_list:shopping_list')

    @staticmethod
    def add_page(request):
        ingredients = Ingredient.objects.all()

        return render(
            request,
            "shopping_list/add_shopping_list.html",
            {"ingredients": ingredients}
        )
