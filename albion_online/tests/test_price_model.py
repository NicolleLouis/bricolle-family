from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import timezone

from albion_online.constants.city import City
from albion_online.models import Object, Price


@pytest.mark.django_db
class TestPriceModel:
    @pytest.fixture
    def albion_object(self):
        return Object.objects.get(aodp_id="T4_MAIN_AXE")

    def test_create_price_for_object(self, albion_object):
        price = Price.objects.create(
            sell_price_min_date=timezone.now(),
            city=City.CAERLEON,
            sell_price_min=1234,
            object=albion_object,
            quality=2,
            sell_price_max=1400,
            sell_price_max_date=timezone.now(),
            buy_price_min=900,
            buy_price_min_date=timezone.now(),
            buy_price_max=1600,
            buy_price_max_date=timezone.now(),
        )

        assert price.object == albion_object
        assert price.city == City.CAERLEON
        assert price.sell_price_min == 1234
        assert price.sell_price == 1234
        assert price.price == 1234
        assert price.buy_price == 1600
        assert price.quality == 2

    def test_quality_cannot_be_greater_than_four(self, albion_object):
        price = Price(
            sell_price_min_date=timezone.now(),
            city=City.BRIDGEWATCH,
            sell_price_min=1234,
            object=albion_object,
            quality=5,
        )

        with pytest.raises(ValidationError):
            price.full_clean()

    @override_settings(USE_TZ=True)
    def test_freshness_levels_follow_age_thresholds(self, albion_object):
        now = timezone.now()
        price = Price(
            sell_price_min_date=now - timedelta(minutes=30),
            sell_price_min=1234,
            city=City.BRIDGEWATCH,
            object=albion_object,
            quality=2,
            buy_price_max_date=now - timedelta(hours=2),
            buy_price_max=1500,
        )

        assert price.sell_price_freshness["label"] == "Info fiable"
        assert price.sell_price_freshness["class_name"] == "bg-success"
        assert price.buy_price_freshness["label"] == "Info > 1 heure"
        assert price.buy_price_freshness["class_name"] == "bg-warning text-dark"
