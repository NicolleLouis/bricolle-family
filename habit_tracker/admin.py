from django.contrib import admin

from habit_tracker.models import Day, Habit, Objective


@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("name", "objective")
    search_fields = ("name", "objective__name")
    list_filter = ("objective",)


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ("date", "habit_list")
    search_fields = ("date", "habits__name")
    filter_horizontal = ("habits",)

    @staticmethod
    def habit_list(obj):
        return ", ".join(obj.habits.values_list("name", flat=True)) or "—"
    habit_list.short_description = "Habitudes"
