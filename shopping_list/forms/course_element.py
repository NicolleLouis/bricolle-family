from django import forms

from shopping_list.models import Course, CourseElement

CourseElementFormSet = forms.inlineformset_factory(
    Course,
    CourseElement,
    fields=['ingredient', 'quantity'],
    extra=1,
    can_delete=True,
    widgets={
        'ingredient': forms.Select(attrs={'class': 'form-select'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    },
    labels={
        'ingredient': 'Ingrédient',
        'quantity': 'Quantité',
    }
)
