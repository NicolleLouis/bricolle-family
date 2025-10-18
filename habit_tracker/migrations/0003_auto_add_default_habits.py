from django.db import migrations
from django.db.utils import OperationalError, ProgrammingError


HABITS = [
    "Séance de sport",
    "Cuisiner un plat",
    "Choisir une recette qui fait envie",
    "Se coucher avant minuit",
    "Savourer",
    "Méditer",
    "Lire",
    "Progresser à un jeux",
    "Réfléchir",
]


def create_habits(apps, schema_editor):
    Habit = apps.get_model("habit_tracker", "Habit")
    try:
        for name in HABITS:
            Habit.objects.get_or_create(name=name)
    except (OperationalError, ProgrammingError):
        return


def delete_habits(apps, schema_editor):
    Habit = apps.get_model("habit_tracker", "Habit")
    try:
        Habit.objects.filter(name__in=HABITS).delete()
    except (OperationalError, ProgrammingError):
        return


class Migration(migrations.Migration):

    dependencies = [
        ("habit_tracker", "0002_auto_add_default_objectives"),
    ]

    operations = [
        migrations.RunPython(create_habits, delete_habits),
    ]
