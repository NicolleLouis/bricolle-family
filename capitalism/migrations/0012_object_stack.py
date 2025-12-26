from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Count


def migrate_objects_to_stacks(apps, schema_editor):
    Object = apps.get_model("capitalism", "Object")
    ObjectStack = apps.get_model("capitalism", "ObjectStack")

    rows = (
        Object.objects.values("owner_id", "type", "in_sale", "price")
        .annotate(quantity=Count("id"))
        .order_by("owner_id", "type", "in_sale", "price")
    )
    stacks = [
        ObjectStack(
            owner_id=row["owner_id"],
            type=row["type"],
            in_sale=row["in_sale"],
            price=row["price"],
            quantity=row["quantity"],
        )
        for row in rows
    ]
    if stacks:
        ObjectStack.objects.bulk_create(stacks, batch_size=500)


class Migration(migrations.Migration):
    dependencies = [
        ("capitalism", "0011_alter_marketperceivedprice_object_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ObjectStack",
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
                ("in_sale", models.BooleanField(default=False)),
                ("price", models.FloatField(blank=True, default=None, null=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("ore", "Ore"),
                            ("wood", "Wood"),
                            ("wheat", "Wheat"),
                            ("flour", "Flour"),
                            ("bread", "Bread"),
                            ("pickaxe", "Pickaxe"),
                            ("axe", "Axe"),
                            ("scythe", "Scythe"),
                            ("spatula", "Spatula"),
                        ],
                        default="bread",
                        max_length=32,
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owned_objects",
                        to="capitalism.human",
                    ),
                ),
            ],
        ),
        migrations.RunPython(migrate_objects_to_stacks, migrations.RunPython.noop),
        migrations.DeleteModel(name="Object"),
    ]
