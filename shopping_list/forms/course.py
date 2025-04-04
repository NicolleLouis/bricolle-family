from django import forms

from shopping_list.models import Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du plat'}),
        }
        labels = {
            'name': 'Nom',
        }
