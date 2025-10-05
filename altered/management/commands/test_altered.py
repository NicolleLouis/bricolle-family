from django.core.management.base import BaseCommand

from altered.services.altered_fetch_unique_price import AlteredFetchUniquePriceService


class Command(BaseCommand):
    help = "Debug"

    def handle(self, *args, **kwargs):
        service = AlteredFetchUniquePriceService()
        service.handle()
