from django.db import migrations
from django.db.utils import OperationalError, ProgrammingError


OBJECTIVE_TO_HABITS = {
    "Être sportif": ["Séance de sport"],
    "Être cuisinier": ["Cuisiner un plat", "Choisir une recette qui fait envie"],
    "Être heureux": ["Se coucher avant minuit", "Savourer", "Méditer"],
    "Être intelligent": ["Lire", "Progresser à un jeux", "Réfléchir"],
}


def assign_objectives(apps, schema_editor):
    Habit = apps.get_model("habit_tracker", "Habit")
    Objective = apps.get_model("habit_tracker", "Objective")
    try:
        for objective_name, habit_names in OBJECTIVE_TO_HABITS.items():
            try:
                objective = Objective.objects.get(name=objective_name)
            except Objective.DoesNotExist:
                continue
            Habit.objects.filter(name__in=habit_names).update(objective=objective)
    except (OperationalError, ProgrammingError):
        return


def unassign_objectives(apps, schema_editor):
    Habit = apps.get_model("habit_tracker", "Habit")
    try:
        Habit.objects.filter(name__in=sum(OBJECTIVE_TO_HABITS.values(), [])).update(objective=None)
    except (OperationalError, ProgrammingError):
        return


class Migration(migrations.Migration):

    dependencies = [
        ("habit_tracker", "0003_auto_add_default_habits"),
    ]

    operations = [
        migrations.RunPython(assign_objectives, unassign_objectives),
    ]
