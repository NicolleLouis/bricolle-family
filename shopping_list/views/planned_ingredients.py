import json

from django.http import HttpResponseBadRequest, JsonResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect

from shopping_list.forms.shopping_list_item import ShoppingListItemForm
from shopping_list.models import ShoppingListItem
from shopping_list.models.ingredient_history import IngredientHistory


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

            shopping_list_item = get_object_or_404(ShoppingListItem, id=planned_ingredient_id)

            IngredientHistory.objects.create(
                ingredient=shopping_list_item.ingredient,
                quantity=shopping_list_item.quantity
            )

            shopping_list_item.delete()

            return JsonResponse({"status": "success", "message": "Item marked as bought and removed from list."})

        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON.")
        except Http404:
            raise
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An unexpected error occurred: {str(e)}"}, status=500)

    @staticmethod
    def add_api(request):
        if request.method == 'POST':
            form = ShoppingListItemForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('shopping_list:shopping_list')
        else:
            form = ShoppingListItemForm()
        return redirect('shopping_list:shopping_list_add_page')

    @staticmethod
    def add_page(request):
        form = ShoppingListItemForm()

        return render(
            request,
            "shopping_list/add_shopping_list.html",
            {"form": form}
        )
