from django import forms

from shopping_list.models import Course, CourseElement, Ingredient

CourseElementFormSet = forms.inlineformset_factory(
    Course,
    CourseElement,
    fields=['ingredient', 'quantity'],
    extra=1,
    can_delete=True,
    widgets={
        'ingredient': forms.Select(attrs={'class': 'form-select'}, choices=Ingredient.objects.order_by('name')),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    },
    labels={
        'ingredient': 'Ingrédient',
        'quantity': 'Quantité',
    }
)
