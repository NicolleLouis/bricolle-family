from django import forms

from sport.models import Training


class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = ["name", "training_targets", "content"]
        widgets = {
            "training_targets": forms.CheckboxSelectMultiple(),
            "content": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["training_targets"].queryset = (
            self.fields["training_targets"].queryset.order_by("name")
        )
        self.fields["training_targets"].label = "Objectifs associés"
