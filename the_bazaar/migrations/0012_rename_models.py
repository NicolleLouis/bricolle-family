from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('the_bazaar', '0011_bazaarseason_version_alter_bazaarseason_name_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BazaarArchetype',
            new_name='Archetype',
        ),
        migrations.RenameModel(
            old_name='BazaarRun',
            new_name='Run',
        ),
        migrations.RenameModel(
            old_name='BazaarSeason',
            new_name='Season',
        ),
    ]