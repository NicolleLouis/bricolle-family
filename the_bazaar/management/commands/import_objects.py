import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from the_bazaar.constants.item_size import ItemSize
from the_bazaar.models import Object


class Command(BaseCommand):
    help = "Import objects from a CSV file located in the_bazaar/data/object_stelle.csv"

    def handle(self, *args, **options):
        csv_path = os.path.join(settings.BASE_DIR, "the_bazaar", "data", "object_stelle.csv")
        if not os.path.exists(csv_path):
            raise CommandError(f"CSV file not found at {csv_path}")

        with open(csv_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 2:
                    self.stderr.write(f"Skipping invalid row: {row}")
                    continue

                name, size_raw = [item.strip() for item in row[:4]]

                size = size_raw.upper()
                if size not in ItemSize.values:
                    raise CommandError(f"Invalid item size '{size_raw}' for object '{name}'")

                Object.objects.update_or_create(
                    name=name,
                    defaults={
                        "size": size,
                        "character": "STELLE",
                    },
                )

        self.stdout.write(self.style.SUCCESS("Objects imported successfully."))
