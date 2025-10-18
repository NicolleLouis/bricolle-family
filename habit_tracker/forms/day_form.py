from django import forms

from habit_tracker.models import Day, Habit


class DayForm(forms.Form):
    date = forms.DateField(
        label="Jour",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    habits = forms.ModelMultipleChoiceField(
        label="Habitudes complétées",
        queryset=Habit.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["habits"].queryset = Habit.objects.order_by("name")
        self.fields["date"].widget.attrs.setdefault("class", "form-control")
        self.fields["habits"].widget.attrs.setdefault("class", "form-check-input me-2")

    def save(self):
        cleaned_data = self.cleaned_data
        day, _created = Day.objects.get_or_create(date=cleaned_data["date"])
        selected_habits = list(cleaned_data["habits"])
        day.habits.set(selected_habits)
        return day
