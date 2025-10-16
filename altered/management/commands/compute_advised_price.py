from django.core.management.base import BaseCommand

from altered.services import ComputeAdvisedPrice


class Command(BaseCommand):
    help = "Compute advised prices for unsold unique flips and update records."

    def handle(self, *args, **options):
        ComputeAdvisedPrice().handle()
        self.stdout.write(self.style.SUCCESS("Advised prices computation completed."))
