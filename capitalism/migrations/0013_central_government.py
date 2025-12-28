from django.db import migrations, models
import django.db.models.deletion


def create_central_governments(apps, schema_editor):
    simulation_model = apps.get_model("capitalism", "Simulation")
    central_government_model = apps.get_model("capitalism", "CentralGovernment")
    existing_simulation_ids = set(
        central_government_model.objects.values_list("simulation_id", flat=True)
    )
    missing_simulations = simulation_model.objects.exclude(id__in=existing_simulation_ids)
    central_government_model.objects.bulk_create(
        [central_government_model(simulation=simulation) for simulation in missing_simulations],
        batch_size=500,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("capitalism", "0012_object_stack"),
    ]

    operations = [
        migrations.CreateModel(
            name="CentralGovernment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("money", models.FloatField(default=150.0)),
                (
                    "simulation",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="central_government",
                        to="capitalism.simulation",
                    ),
                ),
            ],
        ),
        migrations.RunPython(create_central_governments, migrations.RunPython.noop),
    ]
