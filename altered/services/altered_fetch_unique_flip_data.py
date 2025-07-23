from altered.constants.altered_website import AlteredWebsiteConstant
from altered.models import UniqueFlip
import requests


class AlteredFetchUniqueFlipDataService:
    TIMEOUT = 30

    def __init__(self, flip: UniqueFlip):
        self.flip = flip

    def handle(self):
        url = f"{AlteredWebsiteConstant.BASE_URL}/cards/{self.flip.unique_id}?locale=fr-fr"
        try:
            response = requests.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error while fetching unique flip data : {e}")
            return

        data = response.json()
        card = data.get("card", {})
        self.flip.name = card.get("name")
        self.flip.image_path = card.get("imagePath")
        self.flip.save(update_fields=["name", "image_path"])
