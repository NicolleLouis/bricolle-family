import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from helpinglouis.models import Name

class Command(BaseCommand):
    help = "Importe des prénoms depuis un fichier CSV fixe"

    def handle(self, *args, **kwargs):
        fichier_csv = os.path.join(settings.BASE_DIR, "helpinglouis", "data", "prenoms.csv")

        with open(fichier_csv, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                Name.objects.get_or_create(
                    name=row["name"],
                    sex=self.clean_sex(row["sex"]),
                )

    @staticmethod
    def clean_sex(raw_sex):
        if raw_sex == "M":
            return False
        elif raw_sex == "F":
            return True
        else:
            raise ValueError(f"Input not recognized: {raw_sex}")
