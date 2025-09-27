from django.db import migrations


def delete_diaper_changes(apps, schema_editor):
    DiaperChange = apps.get_model("agathe", "DiaperChange")
    DiaperChange.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("agathe", "0007_delete_aspirinintake"),
    ]

    operations = [
        migrations.RunPython(delete_diaper_changes, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="diaperchange",
            name="pooh",
        ),
        migrations.RemoveField(
            model_name="diaperchange",
            name="urine",
        ),
    ]
