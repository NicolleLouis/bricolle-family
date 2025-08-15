# Generated manually
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('the_bazaar', '0022_remove_object_card_set_delete_cardset'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opponent_character', models.CharField(choices=[('DOOLEY', 'Dooley'), ('MAK', 'Mak'), ('PYGMALIEN', 'Pygmalien'), ('STELLE', 'Stelle'), ('VANESSA', 'Vanessa')], max_length=9)),
                ('day_number', models.PositiveIntegerField()),
                ('comment', models.TextField(blank=True)),
                ('opponent_archetype', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='the_bazaar.archetype')),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fights', to='the_bazaar.run')),
            ],
            options={
                'ordering': ['day_number'],
                'unique_together': {('run', 'day_number')},
            },
        ),
    ]
