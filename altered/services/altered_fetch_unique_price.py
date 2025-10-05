import requests

from altered.constants.altered_website import AlteredWebsiteConstant
from altered.models import UniqueFlip


class AlteredFetchUniquePriceService:
    TIMEOUT = 30

    def __init__(self):
        self.uniques_to_check = self.get_uniques_to_check()

    def handle(self):
        for unique in self.uniques_to_check:
            self.fetch_unique_price(unique)

    @staticmethod
    def get_uniques_to_check():
        all_uniques = UniqueFlip.objects.all()
        return [unique for unique in all_uniques if not unique.is_sold]

    @staticmethod
    def price_url(unique: UniqueFlip):
        return f"{AlteredWebsiteConstant.BASE_URL}/cards/{unique.unique_id}/offers"

    def fetch_unique_price(self, unique: UniqueFlip):
        try:
            response = requests.get(self.price_url(unique), timeout=self.TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error while fetching unique flip data : {e}")

        data = response.json()
        print(data)
