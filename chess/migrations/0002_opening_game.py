from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('chess', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Opening',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=500)),
                ('pgn', models.TextField(blank=True, null=True)),
                ('color', models.CharField(choices=[('white', 'Blanc'), ('black', 'Noir')], max_length=5)),
                ('lessons', models.TextField()),
                ('opening', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='games', to='chess.opening')),
            ],
        ),
    ]
