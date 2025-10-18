from django.db import migrations
from django.db.utils import OperationalError, ProgrammingError


OBJECTIVES = [
    "Être sportif",
    "Être cuisinier",
    "Être heureux",
    "Être intelligent",
]


def create_objectives(apps, schema_editor):
    Objective = apps.get_model("habit_tracker", "Objective")
    try:
        for name in OBJECTIVES:
            Objective.objects.get_or_create(name=name)
    except (OperationalError, ProgrammingError):
        # If the table does not exist yet (e.g. initial migration failure), skip.
        return


def delete_objectives(apps, schema_editor):
    Objective = apps.get_model("habit_tracker", "Objective")
    try:
        Objective.objects.filter(name__in=OBJECTIVES).delete()
    except (OperationalError, ProgrammingError):
        return


class Migration(migrations.Migration):

    dependencies = [
        ("habit_tracker", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_objectives, delete_objectives),
    ]
