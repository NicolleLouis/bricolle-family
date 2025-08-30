from datetime import timedelta

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import PitStop
from .services.pit_stop_service import PitStopService


@receiver(pre_save, sender=PitStop)
def limit_pit_stop_duration(sender, instance, **kwargs):
    if instance.start_date and instance.end_date:
        if instance.duration > 60 or instance.duration < 2:
            approximate_duration = PitStopService.get_average_duration(instance)
            instance.end_date = instance.start_date + timedelta(minutes=approximate_duration)
