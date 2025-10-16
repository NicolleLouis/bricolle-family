from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from altered.models import UniqueFlip


class ComputeAdvisedPrice:
    THRESHOLD_MULTIPLIER = Decimal('1.20')
    LOW_PRICE_MAX_AGE = timedelta(days=30)
    HIGH_PRICE_MAX_AGE = timedelta(days=15)
    DISCOUNT_RATIO = Decimal('0.90')
    NO_PRICE_MULTIPLIER = Decimal('3.00')

    def handle(self) -> None:
        unsold_uniques = (
            UniqueFlip.objects.filter(sold_at__isnull=True)
            .prefetch_related('prices')
            .order_by('bought_at')
        )

        above_threshold: list[UniqueFlip] = []
        below_threshold: list[UniqueFlip] = []

        now = timezone.now()

        for flip in unsold_uniques:
            current_price = flip.current_price
            if current_price is None:
                self._set_no_price_advised_price(flip)
            elif Decimal(current_price) >= (flip.bought_price * self.THRESHOLD_MULTIPLIER):
                above_threshold.append(flip)
                self._maybe_update_advised_price(flip, now - self.HIGH_PRICE_MAX_AGE)
            else:
                below_threshold.append(flip)
                self._maybe_update_advised_price(flip, now - self.LOW_PRICE_MAX_AGE)

    def _maybe_update_advised_price(self, flip: UniqueFlip, threshold_date):
        latest_price = flip.prices.first()
        if latest_price is None:
            return

        if latest_price.date >= threshold_date:
            return

        current_price = flip.current_price
        if current_price is None:
            return

        advised_price = (current_price * self.DISCOUNT_RATIO).quantize(Decimal('0.01'))
        if flip.advised_price != advised_price:
            flip.advised_price = advised_price
            flip.save(update_fields=['advised_price'])

    def _set_no_price_advised_price(self, flip: UniqueFlip):
        advised_price = (flip.bought_price * self.NO_PRICE_MULTIPLIER).quantize(Decimal('0.01'))
        if flip.advised_price != advised_price:
            flip.advised_price = advised_price
            flip.save(update_fields=['advised_price'])
