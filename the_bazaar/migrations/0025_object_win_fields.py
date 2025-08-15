from django.db import migrations, models

from the_bazaar.constants.result import Result


def set_best_win(apps, schema_editor):
    Object = apps.get_model('the_bazaar', 'Object')
    for obj in Object.objects.all():
        if obj.was_mastered:
            obj.best_win = Result.GOLD_WIN
        else:
            obj.best_win = None
        obj.save(update_fields=['best_win'])


class Migration(migrations.Migration):

    dependencies = [
        ('the_bazaar', '0024_fight'),
    ]

    operations = [
        migrations.RenameField(
            model_name='object',
            old_name='victory_number',
            new_name='gold_win_number',
        ),
        migrations.AddField(
            model_name='object',
            name='bronze_win_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='object',
            name='silver_win_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='object',
            name='best_win',
            field=models.CharField(choices=Result.choices, max_length=10, null=True, blank=True),
        ),
        migrations.RunPython(set_best_win, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='object',
            name='was_mastered',
        ),
    ]
