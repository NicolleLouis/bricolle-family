from flash_cards.models import Question, ThemePreset


class ThemePresetQuestionFilterService:
    """Filter questions according to a theme preset inclusion/exclusion strategy."""

    def __init__(self, preset: ThemePreset, queryset=None) -> None:
        self.preset = preset
        self.queryset = queryset or Question.objects.all()

    def filter_questions(self):
        category_ids = list(self.preset.categories.values_list("id", flat=True))
        if self.preset.is_exclusion:
            if not category_ids:
                return self.queryset
            return self.queryset.exclude(category_id__in=category_ids)

        if not category_ids:
            return self.queryset.none()
        return self.queryset.filter(category_id__in=category_ids)
