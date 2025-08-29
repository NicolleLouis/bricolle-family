from datetime import timedelta

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import PitStop


@receiver(pre_save, sender=PitStop)
def limit_pit_stop_duration(sender, instance, **kwargs):
    if instance.start_date and instance.end_date:
        if instance.end_date - instance.start_date > timedelta(hours=1):
            instance.end_date = instance.start_date + timedelta(minutes=15)
