from django import forms

from documents.models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "directory", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "directory": forms.Select(attrs={"class": "form-select"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 10}),
        }
        labels = {
            "title": "Titre",
            "directory": "Catégorie",
            "content": "Contenu",
        }
