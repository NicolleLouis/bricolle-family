from django.shortcuts import render, redirect

from shopping_list.exceptions.ingredient import IngredientAlreadyPresent
from shopping_list.forms.ingredient import IngredientForm


def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shopping_list:shopping_list')
        else:
            return render(
                request,
                "shopping_list/error.html",
                {"message": "Ingredient already present in database"}
            )
    else:
        form = IngredientForm()
    return render(request, 'shopping_list/add_ingredient.html', {'form': form})
