from django.core.management.base import BaseCommand

from agathe.models import PitStop


class Command(BaseCommand):
    help = "Update all deck data from altered website"

    def handle(self, *args, **kwargs):
        stops = PitStop.objects.all().order_by('start_date')
        for stop in stops:
            stop.save()
