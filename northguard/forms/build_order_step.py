from django import forms

from northguard.models import BuildOrder
from northguard.models.build_order_step import BuildOrderStep


class BuildOrderStepForm(forms.ModelForm):
    class Meta:
        model = BuildOrderStep
        fields = ['milestone']
        widgets = {
            'milestone': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'milestone': 'Milestone',
        }


BuildOrderStepFormSet = forms.inlineformset_factory(
    BuildOrder,
    BuildOrderStep,
    form=BuildOrderStepForm,
    extra=1,
    can_delete=True,
    can_order=True
)
