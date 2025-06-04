import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from the_bazaar.constants.character import Character
from the_bazaar.constants.item_size import ItemSize
from the_bazaar.models import CardSet, Object


class Command(BaseCommand):
    help = "Import objects from a CSV file located in the_bazaar/data/object.csv"

    def handle(self, *args, **options):
        csv_path = os.path.join(settings.BASE_DIR, "the_bazaar", "data", "object.csv")
        if not os.path.exists(csv_path):
            raise CommandError(f"CSV file not found at {csv_path}")

        with open(csv_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.reader(csvfile)
            # Skip header if present
            header = next(reader, None)
            for row in reader:
                if len(row) < 4:
                    self.stderr.write(f"Skipping invalid row: {row}")
                    continue

                name, size_raw, card_set_name, character_raw = [item.strip() for item in row[:4]]

                size = size_raw.upper()
                if size not in ItemSize.values:
                    raise CommandError(f"Invalid item size '{size_raw}' for object '{name}'")

                character = character_raw.upper()
                if character not in Character.values:
                    raise CommandError(f"Invalid character '{character_raw}' for object '{name}'")

                try:
                    card_set = CardSet.objects.get(name=card_set_name)
                except CardSet.DoesNotExist as exc:
                    raise CommandError(f'Card set "{card_set_name}" not found for object "{name}"') from exc

                Object.objects.update_or_create(
                    name=name,
                    defaults={
                        "size": size,
                        "character": character,
                        "card_set": card_set,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Objects imported successfully."))
