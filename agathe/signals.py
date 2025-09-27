from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PitStop


@receiver(post_save, sender=PitStop)
def compute_delay_before_next_pit_stop(sender, instance, **kwargs):
    previous_stop = (
        PitStop.objects.filter(start_date__lt=instance.start_date)
        .order_by("-start_date")
        .first()
    )
    if previous_stop:
        delay = int(
            (instance.start_date - previous_stop.start_date).total_seconds() / 60
        )
        PitStop.objects.filter(pk=previous_stop.pk).update(
            delay_before_next_pit_stop=delay
        )

    next_stop = (
        PitStop.objects.filter(start_date__gt=instance.start_date)
        .order_by("start_date")
        .first()
    )
    if next_stop:
        delay = int((next_stop.start_date - instance.start_date).total_seconds() / 60)
        PitStop.objects.filter(pk=instance.pk).update(
            delay_before_next_pit_stop=delay
        )
