from django import forms

from babyberon.models import BabyBottle


class BabyBottleForm(forms.ModelForm):
    class Meta:
        model = BabyBottle
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité en mL'}),
        }
        labels = {
            'quantity': 'Quantité (mL)',
        }
