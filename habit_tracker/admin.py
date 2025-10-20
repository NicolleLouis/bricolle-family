from django.contrib import admin

from habit_tracker.models import Day, Habit, Objective


@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    list_display = ("name", "check_frequency", "objective_duration")
    search_fields = ("name",)
    list_filter = ("check_frequency",)


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("name", "objective", "check_frequency", "objective_in_frequency")
    search_fields = ("name", "objective__name")
    list_filter = ("objective", "check_frequency")


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ("date", "habit_list")
    search_fields = ("date", "habits__name")
    filter_horizontal = ("habits",)

    @staticmethod
    def habit_list(obj):
        return ", ".join(obj.habits.values_list("name", flat=True)) or "—"
    habit_list.short_description = "Habitudes"
