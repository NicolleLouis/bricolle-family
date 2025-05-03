from django import forms

from shopping_list.models import ShoppingListItem, Ingredient


class ShoppingListItemForm(forms.Form):
    ingredient_id = forms.ModelChoiceField(
        queryset=Ingredient.objects.all(),
        empty_label="-------",
        label="Ingrédient:",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'ingredient-choice'})
    )
    ingredient_quantity = forms.DecimalField(
        min_value=0.01,
        initial=1,
        label="Quantitée:",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'ingredient-quantity'})
    )

    def save(self):
        ingredient = self.cleaned_data['ingredient_id']
        quantity = self.cleaned_data['ingredient_quantity']

        planned_ingredient, created = ShoppingListItem.objects.get_or_create(
            ingredient=ingredient,
            defaults={'quantity': quantity}
        )
        if not created:
            planned_ingredient.quantity += quantity
            planned_ingredient.save()

        return planned_ingredient