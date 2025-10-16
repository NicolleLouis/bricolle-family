from django.core.management.base import BaseCommand

from altered.services import ComputeAdvisedPrice


class Command(BaseCommand):
    help = "Debug"

    def handle(self, *args, **kwargs):
        ComputeAdvisedPrice().handle()
        self.stdout.write(self.style.SUCCESS("Advised prices computation completed."))