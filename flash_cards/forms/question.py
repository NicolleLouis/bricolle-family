import json

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
        fields = ["category", "text", "explanation"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Entrez la question…",
                }
            ),
            "explanation": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                    "placeholder": "Ajoutez une explication détaillée (optionnel)…",
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


class JsonQuestionForm(forms.Form):
    payload = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 14,
                "class": "form-control font-monospace",
                "placeholder": '{\n  "question": "...",\n  "category": "...",\n  "positive_answers": ["..."],\n  "negative_answers": ["..."]\n}',
            }
        ),
        label="Contenu JSON",
        help_text="Utilisez le même format que l'API /flash_cards/api/questions/.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parsed_payload: dict | None = None

    def clean(self):
        cleaned_data = super().clean()
        payload_text = cleaned_data.get("payload")
        if not payload_text:
            return cleaned_data
        try:
            parsed = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError(f"JSON invalide : {exc.msg}") from exc
        if not isinstance(parsed, dict):
            raise forms.ValidationError("Le JSON doit représenter un objet.")
        self._parsed_payload = parsed
        return cleaned_data

    @property
    def parsed_payload(self) -> dict | None:
        return self._parsed_payload
