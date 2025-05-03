import json

from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from shopping_list.forms.shopping_list_item import ShoppingListItemForm
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
        if request.method == 'POST':
            form = ShoppingListItemForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('shopping_list:shopping_list')
        else:
            form = ShoppingListItemForm()

        return redirect('shopping_list:shopping_list_add')

    @staticmethod
    def add_page(request):
        form = ShoppingListItemForm()

        return render(
            request,
            "shopping_list/add_shopping_list.html",
            {"form": form}
        )
