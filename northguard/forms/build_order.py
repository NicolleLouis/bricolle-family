from django import forms

from northguard.models import BuildOrder


class BuildOrderForm(forms.ModelForm):
    class Meta:
        model = BuildOrder
        fields = ['name', 'clan', 'state_of_the_art']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du build order'}),
            'clan': forms.Select(attrs={'class': 'form-control'}),
            'state_of_the_art': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nom',
            'clan': 'Clan',
            'state_of_the_art': 'Template',
        }
