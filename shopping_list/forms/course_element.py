from django import forms

from shopping_list.models import Course, CourseElement, Ingredient

class CourseElementForm(forms.ModelForm):
    class Meta:
        model = CourseElement
        fields = ['ingredient', 'quantity']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'ingredient': 'Ingrédient',
            'quantity': 'Quantité',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].queryset = Ingredient.objects.order_by('name')

CourseElementFormSet = forms.inlineformset_factory(
    Course,
    CourseElement,
    form=CourseElementForm,
    extra=1,
    can_delete=True,
)
