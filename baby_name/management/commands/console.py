import time

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Random stuff"

    def handle(self, *args, **kwargs):
        start_time = time.time()
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")