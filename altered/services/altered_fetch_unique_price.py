import requests
from django.db.models import Max

from altered.models import UniqueFlip


class AlteredFetchUniquePriceService:
    TIMEOUT = 30
    PRICE_URL = "https://api.altered.gg/public/cards/{unique_id}/offers/"
    LOCALE = "en-us"
    USER_AGENT = "Bricolle Family (contact: louisxnicolle@gmail.com)"

    def __init__(self):
        self.uniques_to_check = self.get_uniques_to_check()

    def handle(self):
        for unique in self.uniques_to_check:
            self.fetch_unique_price(unique)

    @staticmethod
    def get_uniques_to_check():
        uniques = (
            UniqueFlip.objects.filter(sold_price__isnull=True)
            .annotate(latest_price_date=Max('prices__date'))
            .order_by('latest_price_date', 'bought_at')
        )
        return list(uniques[:60])

    @classmethod
    def price_url(cls, unique: UniqueFlip) -> str:
        return cls.PRICE_URL.format(unique_id=unique.unique_id)

    @classmethod
    def get_headers(cls):
        return {
            "accept": "application/ld+json",
            "Accept-Language": cls.LOCALE,
            "User-Agent": cls.USER_AGENT,
        }

    @classmethod
    def get_parameters(cls):
        return {
            "locale": cls.LOCALE,
            # "page": 1,
            # "itemsPerPage": 1,
        }

    def fetch_unique_price(self, unique: UniqueFlip):
        try:
            response = requests.get(
                self.price_url(unique),
                timeout=self.TIMEOUT,
                headers=self.get_headers(),
                params=self.get_parameters(),
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error while fetching unique flip data : {e}")

        data = response.json()
        print(data)
