from django import forms

from shopping_list.models import Ingredient


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'is_pantry_staples', 'unit', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'ingrédient'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unité (ex: g, ml...)'}),
            'is_pantry_staples': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Nom',
            'unit': 'Unité',
            'is_pantry_staples': 'Fond de maison',
            'category': 'Catégorie',
        }
