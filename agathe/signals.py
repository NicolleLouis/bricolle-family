from datetime import timedelta

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import PitStop
from .services.pit_stop_service import PitStopService


@receiver(pre_save, sender=PitStop)
def limit_pit_stop_duration(sender, instance, **kwargs):
    if instance.start_date and instance.end_date:
        if instance.duration > 60 or instance.duration < 2:
            approximate_duration = PitStopService.get_average_duration(instance)
            instance.end_date = instance.start_date + timedelta(minutes=approximate_duration)

@receiver(post_save, sender=PitStop)
def compute_delay_before_next_pit_stop(sender, instance, **kwargs):
    missing_delay_pit_stops = PitStop.objects.filter(delay_before_next_pit_stop__isnull=True)
    for pit_stop in missing_delay_pit_stops:
        next_stop = PitStopService.get_next_closest_pit_stop(pit_stop)
        if next_stop is not None and pit_stop.end_date is not None:
            delay = int((next_stop.start_date - pit_stop.end_date).total_seconds() / 60)
            pit_stop.delay_before_next_pit_stop = delay
            pit_stop.save()
