# Generated by Django 4.2.20 on 2025-04-10 16:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('the_bazaar', '0006_remove_bazaarrun_archetype'),
    ]

    operations = [
        migrations.CreateModel(
            name='BazaarArchetype',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=18)),
                ('character', models.CharField(choices=[('DOOLEY', 'Dooley'), ('MAK', 'Mak'), ('PYGMALIEN', 'Pygmalien'), ('VANESSA', 'Vanessa')], default='VANESSA', max_length=9)),
            ],
        ),
        migrations.AddField(
            model_name='bazaarrun',
            name='archetype',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='the_bazaar.bazaararchetype'),
        ),
    ]
