import logging
from datetime import datetime, timezone
import time
from urllib.parse import urlencode

import requests

from albion_online.constants.city import City
from albion_online.models import Object, Price

logger = logging.getLogger(__name__)


class AlbionOnlineDataPriceFetcher:
    BASE_URL = "https://europe.albion-online-data.com"
    PRICES_PATH_TEMPLATE = "/api/v2/stats/prices/{item_ids}.json"
    MAX_URL_LENGTH = 4096
    API_QUALITY_OFFSET = 1
    API_CITY_TO_CITY = {
        "Bridgewatch": City.BRIDGEWATCH,
        "Caerleon": City.CAERLEON,
        "Fort Sterling": City.FORT_STERLING,
        "Lymhurst": City.LYMHURST,
        "Martlock": City.MARTLOCK,
        "Thetford": City.THETFORD,
        "Brecilien": City.BRECILIEN,
    }

    def __init__(self, session=None, clock=None, sleeper=None):
        self._session = session or requests.Session()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._sleep = sleeper or time.sleep
        self.last_request_at = None

    def fetch_current_prices(
        self,
        objects,
        locations: list[str] | None = None,
        qualities: list[int] | None = None,
    ) -> list[Price]:
        object_by_aodp_id = {albion_object.aodp_id: albion_object for albion_object in objects}
        if not object_by_aodp_id:
            return []

        created_prices = []
        for object_batch in self._build_object_batches(list(object_by_aodp_id.values()), locations, qualities):
            payload = self._fetch_price_payload(object_batch, locations, qualities)
            prices = self._build_prices_from_payload(payload, object_by_aodp_id)
            created_prices.extend(Price.objects.bulk_create(prices, batch_size=500))
        return created_prices

    def _fetch_price_payload(self, objects: list[Object], locations, qualities):
        url = self._build_url(objects, locations, qualities)
        logger.info(
            "Albion Online Data request url=%s item_ids=%s",
            url,
            [albion_object.aodp_id for albion_object in objects],
        )
        self._sleep_until_rate_limit()
        self.last_request_at = self._clock()
        response = self._session.get(url, timeout=30)
        response.raise_for_status()
        return response.json()

    def _build_object_batches(self, objects: list[Object], locations, qualities) -> list[list[Object]]:
        batches = []
        current_batch = []
        for albion_object in objects:
            candidate_batch = [*current_batch, albion_object]
            if current_batch and len(self._build_url(candidate_batch, locations, qualities)) > self.MAX_URL_LENGTH:
                batches.append(current_batch)
                current_batch = [albion_object]
            else:
                current_batch = candidate_batch

        if current_batch:
            batches.append(current_batch)
        return batches

    def _build_url(self, objects: list[Object], locations, qualities) -> str:
        item_ids = ",".join(albion_object.aodp_id for albion_object in objects)
        url = f"{self.BASE_URL}{self.PRICES_PATH_TEMPLATE.format(item_ids=item_ids)}"
        query_params = self._build_query_params(locations, qualities)
        if query_params:
            url = f"{url}?{urlencode(query_params)}"
        return url

    def _build_query_params(self, locations, qualities):
        query_params = {}
        if locations:
            query_params["locations"] = ",".join(locations)
        if qualities:
            query_params["qualities"] = ",".join(str(quality) for quality in qualities)
        return query_params

    def _build_prices_from_payload(self, payload, object_by_aodp_id: dict[str, Object]) -> list[Price]:
        prices = []
        for price_data in payload:
            price = self._build_price(price_data, object_by_aodp_id)
            if price is not None:
                prices.append(price)
        return prices

    def _build_price(self, price_data, object_by_aodp_id: dict[str, Object]) -> Price | None:
        albion_object = object_by_aodp_id.get(price_data.get("item_id"))
        city = self.API_CITY_TO_CITY.get(price_data.get("city"))
        quality = self._convert_api_quality(price_data.get("quality"))
        sell_price_min_date = self._parse_timestamp(price_data.get("sell_price_min_date"))
        if albion_object is None or city is None or quality is None or sell_price_min_date is None:
            return None

        return Price(
            object=albion_object,
            city=city,
            quality=quality,
            sell_price_min=price_data.get("sell_price_min", 0),
            sell_price_min_date=sell_price_min_date,
            sell_price_max=price_data.get("sell_price_max"),
            sell_price_max_date=self._parse_timestamp(price_data.get("sell_price_max_date")),
            buy_price_min=price_data.get("buy_price_min"),
            buy_price_min_date=self._parse_timestamp(price_data.get("buy_price_min_date")),
            buy_price_max=price_data.get("buy_price_max"),
            buy_price_max_date=self._parse_timestamp(price_data.get("buy_price_max_date")),
        )

    def _convert_api_quality(self, api_quality) -> int | None:
        if api_quality is None:
            return None
        quality = int(api_quality) - self.API_QUALITY_OFFSET
        if quality < 0 or quality > 4:
            return None
        return quality

    def _parse_timestamp(self, timestamp: str | None) -> datetime | None:
        if not timestamp or timestamp.startswith("0001-01-01"):
            return None
        return datetime.fromisoformat(timestamp)

    def _sleep_until_rate_limit(self):
        if self.last_request_at is None:
            return

        elapsed_seconds = (self._clock() - self.last_request_at).total_seconds()
        sleep_duration = 1 - elapsed_seconds
        if sleep_duration > 0:
            self._sleep(sleep_duration)
