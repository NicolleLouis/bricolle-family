from django import forms

from shopping_list.models import CourseHistory


class CourseHistoryForm(forms.ModelForm):
    class Meta:
        model = CourseHistory
        fields = ["rating", "notes"]
        widgets = {
            "rating": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 10}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "rating": "Score",
            "notes": "Commentaire",
        }
