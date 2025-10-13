from django.db import migrations, models


def migrate_training_types_to_targets(apps, schema_editor):
    Training = apps.get_model("sport", "Training")
    TrainingType = apps.get_model("sport", "TrainingType")
    TrainingTarget = apps.get_model("sport", "TrainingTarget")

    for training_type in TrainingType.objects.all():
        target, _ = TrainingTarget.objects.get_or_create(name=training_type.name)
        trainings = training_type.trainings.all()
        for training in trainings:
            training.training_targets.add(target)


class Migration(migrations.Migration):

    dependencies = [
        ("sport", "0004_trainingtarget"),
    ]

    operations = [
        migrations.AddField(
            model_name="training",
            name="training_targets",
            field=models.ManyToManyField(
                blank=True, related_name="trainings", to="sport.trainingtarget"
            ),
        ),
        migrations.RunPython(
            migrate_training_types_to_targets,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="training",
            name="training_types",
        ),
        migrations.DeleteModel(
            name="TrainingType",
        ),
    ]
