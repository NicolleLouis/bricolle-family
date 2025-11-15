from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from flash_cards.models import Answer, Category, Question


class QuestionForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.order_by("name"),
        empty_label="Choisir une catégorie",
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Catégorie",
    )

    class Meta:
        model = Question
        fields = ["category", "text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Entrez la question…",
                }
            ),
        }


class BaseAnswerFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        has_answer = False

        for form in self.forms:
            if getattr(form, "cleaned_data", None) is None:
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            text = form.cleaned_data.get("text", "").strip()
            if text:
                has_answer = True

        if not has_answer:
            raise forms.ValidationError("Ajoutez au moins une réponse.")


AnswerFormSet = inlineformset_factory(
    Question,
    Answer,
    formset=BaseAnswerFormSet,
    fields=("text", "is_correct"),
    extra=1,
    can_delete=True,
    widgets={
        "text": forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Réponse"}
        ),
        "is_correct": forms.CheckboxInput(attrs={"class": "form-check-input"}),
    },
)
