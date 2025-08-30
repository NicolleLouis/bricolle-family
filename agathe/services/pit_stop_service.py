import statistics

from agathe.models import PitStop


class PitStopService:
    SAMPLE_SIZE = 10

    @classmethod
    def get_average_duration(cls, pit_stop: PitStop):
        previous_stops = PitStop.objects.filter(
            start_date__lt=pit_stop.start_date
        ).order_by('-start_date')[:cls.SAMPLE_SIZE]
        durations = [stop.duration for stop in previous_stops]
        return round(statistics.fmean(durations), 0)

    @staticmethod
    def get_next_closest_pit_stop(pit_stop: PitStop):
        if pit_stop.end_date is None:
            return None
        next_stops = PitStop.objects.filter(
            start_date__gt=pit_stop.end_date
        ).order_by('start_date')
        if len(next_stops) == 0:
            return None
        return next_stops[0]
