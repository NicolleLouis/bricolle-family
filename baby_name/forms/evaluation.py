from django import forms

from baby_name.models import Evaluation


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['name', 'score']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-select'}),
            'score': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': 'Prénom',
            'score': 'Vote',
        }
