import json
from datetime import datetime, timezone

import pytest
import requests

from albion_online.constants.city import City
from albion_online.models import AodpRequestLog, Object, Price
from albion_online.services.price_fetcher import AlbionOnlineDataPriceFetcher


class FakeResponse:
    def __init__(self, payload, text=None, status_code=200, raise_for_status_error=None):
        self._payload = payload
        self.text = text if text is not None else json.dumps(payload)
        self.status_code = status_code
        self._raise_for_status_error = raise_for_status_error

    def raise_for_status(self):
        if self._raise_for_status_error is not None:
            raise self._raise_for_status_error
        return None

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.requested_urls = []

    def get(self, url, timeout):
        self.requested_urls.append(url)
        return FakeResponse(self.payload)


class FakeClock:
    def __init__(self, moments):
        self._moments = list(moments)

    def __call__(self):
        return self._moments.pop(0)


class FakeRequestLogService:
    def __init__(self):
        self.logged_requests = []

    def purge_expired(self):
        raise RuntimeError("purge failed")

    def _create_log(self, **kwargs):
        self.logged_requests.append(kwargs)
        return kwargs


@pytest.mark.django_db
class TestAlbionOnlineDataPriceFetcher:
    def test_fetch_current_prices_persists_sell_min_prices(self):
        albion_object = Object.objects.get(aodp_id="T4_BAG")
        session = FakeSession(
            [
                {
                    "item_id": "T4_BAG",
                    "city": "Bridgewatch",
                    "quality": 2,
                    "sell_price_min": 4873,
                    "sell_price_min_date": "2026-04-26T18:05:00",
                    "sell_price_max": 5000,
                    "sell_price_max_date": "2026-04-26T18:05:00",
                    "buy_price_min": 4300,
                    "buy_price_min_date": "2026-04-26T18:05:00",
                    "buy_price_max": 4700,
                    "buy_price_max_date": "2026-04-26T18:05:00",
                },
            ]
        )

        prices = AlbionOnlineDataPriceFetcher(session=session).fetch_current_prices(
            [albion_object],
            locations=["Bridgewatch"],
            qualities=[2],
        )

        assert len(prices) == 1
        price = Price.objects.get()
        assert price.object == albion_object
        assert price.city == City.BRIDGEWATCH
        assert price.quality == 1
        assert price.sell_price_min == 4873
        assert price.sell_price_max == 5000
        assert price.buy_price_min == 4300
        assert price.buy_price_max == 4700
        assert price.sell_price_min_date.isoformat() == "2026-04-26T18:05:00"
        assert price.buy_price_max_date.isoformat() == "2026-04-26T18:05:00"
        log = AodpRequestLog.objects.get()
        assert log.source == "price_fetcher"
        assert log.request_query_string == "locations=Bridgewatch&qualities=2"
        assert log.response_status_code == 200
        assert log.response_body_raw == json.dumps(
            [
                {
                    "item_id": "T4_BAG",
                    "city": "Bridgewatch",
                    "quality": 2,
                    "sell_price_min": 4873,
                    "sell_price_min_date": "2026-04-26T18:05:00",
                    "sell_price_max": 5000,
                    "sell_price_max_date": "2026-04-26T18:05:00",
                    "buy_price_min": 4300,
                    "buy_price_min_date": "2026-04-26T18:05:00",
                    "buy_price_max": 4700,
                    "buy_price_max_date": "2026-04-26T18:05:00",
                },
            ]
        )
        assert log.is_error is False
        assert session.requested_urls == [
            "https://europe.albion-online-data.com/api/v2/stats/prices/T4_BAG.json?locations=Bridgewatch&qualities=2"
        ]

    def test_fetch_current_prices_logs_request(self, caplog):
        albion_object = Object.objects.get(aodp_id="T4_BAG")
        session = FakeSession(
            [
                {
                    "item_id": "T4_BAG",
                    "city": "Bridgewatch",
                    "quality": 2,
                    "sell_price_min": 4873,
                    "sell_price_min_date": "2026-04-26T18:05:00",
                },
            ]
        )

        with caplog.at_level("INFO", logger="albion_online"):
            AlbionOnlineDataPriceFetcher(session=session).fetch_current_prices(
                [albion_object],
                locations=["Bridgewatch"],
                qualities=[2],
            )

        assert any("Albion Online Data request url=" in record.message for record in caplog.records)
        assert any("T4_BAG" in record.message for record in caplog.records)

    def test_fetch_current_prices_records_error_responses(self):
        albion_object = Object.objects.get(aodp_id="T4_BAG")

        class ErrorSession:
            def __init__(self):
                self.requested_urls = []

            def get(self, url, timeout):
                self.requested_urls.append(url)
                response = FakeResponse(
                    [],
                    text='{"detail":"boom"}',
                    status_code=500,
                    raise_for_status_error=requests.HTTPError("500 Server Error"),
                )
                return response

        session = ErrorSession()

        with pytest.raises(requests.HTTPError):
            AlbionOnlineDataPriceFetcher(session=session).fetch_current_prices([albion_object])

        log = AodpRequestLog.objects.get()
        assert log.is_error is True
        assert log.response_status_code == 500
        assert log.response_body_raw == '{"detail":"boom"}'
        assert "500 Server Error" in log.error_message
        assert session.requested_urls == [
            "https://europe.albion-online-data.com/api/v2/stats/prices/T4_BAG.json"
        ]

    def test_fetch_current_prices_keeps_going_when_purge_fails(self):
        albion_object = Object.objects.get(aodp_id="T4_BAG")
        session = FakeSession(
            [
                {
                    "item_id": "T4_BAG",
                    "city": "Bridgewatch",
                    "quality": 2,
                    "sell_price_min": 4873,
                    "sell_price_min_date": "2026-04-26T18:05:00",
                },
            ]
        )

        fetcher = AlbionOnlineDataPriceFetcher(session=session, request_log_service=FakeRequestLogService())

        prices = fetcher.fetch_current_prices([albion_object])

        assert len(prices) == 1
        assert session.requested_urls == [
            "https://europe.albion-online-data.com/api/v2/stats/prices/T4_BAG.json"
        ]

    def test_fetch_current_prices_without_filters_omits_query_string(self):
        albion_object = Object.objects.get(aodp_id="T4_BAG")
        session = FakeSession([])

        AlbionOnlineDataPriceFetcher(session=session).fetch_current_prices([albion_object])

        assert session.requested_urls == [
            "https://europe.albion-online-data.com/api/v2/stats/prices/T4_BAG.json"
        ]

    def test_fetch_current_prices_skips_unknown_cities_and_invalid_qualities(self):
        albion_object = Object.objects.get(aodp_id="T4_BAG")
        session = FakeSession(
            [
                {
                    "item_id": "T4_BAG",
                    "city": "Bridgewatch",
                    "quality": 2,
                    "sell_price_min": 0,
                    "sell_price_min_date": "2026-04-26T18:05:00",
                    "sell_price_max": 1,
                    "sell_price_max_date": "2026-04-26T18:05:00",
                    "buy_price_min": 0,
                    "buy_price_min_date": "2026-04-26T18:05:00",
                    "buy_price_max": 2,
                    "buy_price_max_date": "2026-04-26T18:05:00",
                },
                {
                    "item_id": "T4_BAG",
                    "city": "Unknown City",
                    "quality": 2,
                    "sell_price_min": 1000,
                    "sell_price_min_date": "2026-04-26T18:05:00",
                },
                {
                    "item_id": "T4_BAG",
                    "city": "Bridgewatch",
                    "quality": 6,
                    "sell_price_min": 1000,
                    "sell_price_min_date": "2026-04-26T18:05:00",
                },
                {
                    "item_id": "T4_BAG",
                    "city": "Bridgewatch",
                    "quality": 2,
                    "sell_price_min": 1000,
                    "sell_price_min_date": "0001-01-01T00:00:00",
                },
            ]
        )

        prices = AlbionOnlineDataPriceFetcher(session=session).fetch_current_prices([albion_object])

        assert len(prices) == 1
        price = Price.objects.get()
        assert price.sell_price_min == 0
        assert price.sell_price_max == 1
        assert price.buy_price_max == 2
        assert Price.objects.count() == 1

    def test_fetch_current_prices_supports_brecilien(self):
        albion_object = Object.objects.get(aodp_id="T4_BAG")
        session = FakeSession(
            [
                {
                    "item_id": "T4_BAG",
                    "city": "Brecilien",
                    "quality": 5,
                    "sell_price_min": 1000,
                    "sell_price_min_date": "2026-04-26T18:05:00",
                },
            ]
        )

        AlbionOnlineDataPriceFetcher(session=session).fetch_current_prices([albion_object])

        price = Price.objects.get()
        assert price.city == City.BRECILIEN
        assert price.quality == 4

    def test_fetch_current_prices_supports_multiple_objects_in_one_request(self):
        mercenary_jackets = list(
            Object.objects.filter(aodp_id__contains="ARMOR_LEATHER_SET1").order_by("aodp_id")[:2]
        )
        assert len(mercenary_jackets) == 2
        session = FakeSession(
            [
                {
                    "item_id": mercenary_jackets[0].aodp_id,
                    "city": "Bridgewatch",
                    "quality": 2,
                    "sell_price_min": 1000,
                    "sell_price_min_date": "2026-04-26T18:05:00",
                },
                {
                    "item_id": mercenary_jackets[1].aodp_id,
                    "city": "Bridgewatch",
                    "quality": 2,
                    "sell_price_min": 2000,
                    "sell_price_min_date": "2026-04-26T18:05:00",
                },
            ]
        )

        AlbionOnlineDataPriceFetcher(session=session).fetch_current_prices(mercenary_jackets)

        assert session.requested_urls == [
            f"https://europe.albion-online-data.com/api/v2/stats/prices/{mercenary_jackets[0].aodp_id},{mercenary_jackets[1].aodp_id}.json"
        ]

    def test_fetch_current_prices_waits_only_for_remaining_rate_limit_window(self):
        mercenary_jackets = list(
            Object.objects.filter(aodp_id__contains="ARMOR_LEATHER_SET1").order_by("aodp_id")[:2]
        )
        assert len(mercenary_jackets) == 2
        session = FakeSession(
            [
                {
                    "item_id": mercenary_jackets[0].aodp_id,
                    "city": "Bridgewatch",
                    "quality": 2,
                    "sell_price_min": 1000,
                    "sell_price_min_date": "2026-04-26T18:05:00",
                },
                {
                    "item_id": mercenary_jackets[1].aodp_id,
                    "city": "Bridgewatch",
                    "quality": 2,
                    "sell_price_min": 2000,
                    "sell_price_min_date": "2026-04-26T18:05:00",
                },
            ]
        )
        slept_durations = []
        clock = FakeClock(
            [
                datetime(2026, 4, 26, 18, 5, 0, tzinfo=timezone.utc),
                datetime(2026, 4, 26, 18, 5, 0, tzinfo=timezone.utc),
                datetime(2026, 4, 26, 18, 5, 0, tzinfo=timezone.utc),
                datetime(2026, 4, 26, 18, 5, 1, tzinfo=timezone.utc),
            ]
        )

        fetcher = AlbionOnlineDataPriceFetcher(session=session, clock=clock, sleeper=slept_durations.append)
        fetcher.MAX_URL_LENGTH = 10

        fetcher.fetch_current_prices(mercenary_jackets)

        assert slept_durations == [1.0]
        assert len(session.requested_urls) == 2
