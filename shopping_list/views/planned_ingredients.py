import json

from django.http import HttpResponseBadRequest, JsonResponse, Http404 # Add Http404
from django.shortcuts import get_object_or_404, render, redirect

from shopping_list.forms.shopping_list_item import ShoppingListItemForm
from shopping_list.models import ShoppingListItem, Ingredient # Existing imports
from shopping_list.models.ingredient_history import IngredientHistory # New import


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

            # Create IngredientHistory record before deleting the item
            IngredientHistory.objects.create(
                ingredient=shopping_list_item.ingredient,
                quantity=shopping_list_item.quantity
                # bought_date is handled by default=timezone.now or auto_now_add=True in the model
            )

            shopping_list_item.delete()

            return JsonResponse({"status": "success", "message": "Item marked as bought and removed from list."})

        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON.")
        except Http404: # Let Django handle Http404 by re-raising or not catching it here if it's outside
            raise
        except Exception as e: # Optional: More general exception handling for robustness
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
        # Corrected redirect to the page that displays the form
        return redirect('shopping_list:shopping_list_add_page')

    @staticmethod
    def add_page(request):
        form = ShoppingListItemForm()

        return render(
            request,
            "shopping_list/add_shopping_list.html",
            {"form": form}
        )
