from django.db.models.signals import post_save
from django.dispatch import receiver

from altered.models import UniqueFlip
from altered.services import AlteredFetchUniqueFlipDataService


@receiver(post_save, sender=UniqueFlip)
def fetch_unique_flip_data(sender, instance, created, **kwargs):
    if created:
        AlteredFetchUniqueFlipDataService(instance).handle()
