from django import forms

from games_collection.models import MarkdownDocument


class MarkdownDocumentForm(forms.ModelForm):
    class Meta:
        model = MarkdownDocument
        fields = ["title", "game", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "game": forms.Select(attrs={"class": "form-select"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 10}),
        }
        labels = {
            "title": "Titre",
            "game": "Jeu",
            "content": "Contenu",
        }
