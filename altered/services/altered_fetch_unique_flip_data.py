from altered.constants.altered_website import AlteredWebsiteConstant
from altered.constants.faction import Faction
from altered.models import UniqueFlip
import requests


class AlteredFetchUniqueFlipDataService:
    TIMEOUT = 30

    def __init__(self, unique: UniqueFlip):
        self.unique = unique
        self.data = None

    def fetch_data(self):
        url = f"{AlteredWebsiteConstant.BASE_URL}/cards/{self.unique.unique_id}?locale=fr-fr"
        try:
            response = requests.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error while fetching unique flip data : {e}")

        self.data = response.json()

    def handle(self):
        self.fetch_data()
        print(self.data)
        self.unique.faction = self.find_faction()
        self.unique.name = self.data["name"]
        self.unique.image_path = self.get_image_path()
        update_fields = ["name", "image_path", "faction"]

        self.unique.save(update_fields=update_fields)

        self.update_elements()

    def get_image_path(self):
        if "imagePath" in self.data:
            return self.data["imagePath"]

        if "allImagePath" in self.data:
            all_image_data = self.data["allImagePath"]
            if all_image_data['fr-fr'] is not None:
                return all_image_data['fr-fr']
            return all_image_data['en-us']
        return None


    def find_faction(self):
        raw_faction_name = self.data["mainFaction"]["name"]
        for faction in Faction:
            if raw_faction_name.lower() == faction.name.lower():
                return faction
        raise ValueError("Faction Not found")

    def update_elements(self):
        raw_elements = self.data["elements"]
        self.unique.main_cost = raw_elements["MAIN_COST"]
        self.unique.recall_cost = raw_elements["RECALL_COST"]
        self.unique.mountain_power = raw_elements["MOUNTAIN_POWER"]
        self.unique.ocean_power = raw_elements["OCEAN_POWER"]
        self.unique.forest_power = raw_elements["FOREST_POWER"]
        self.unique.save(update_fields=[
            "main_cost",
            "recall_cost",
            "mountain_power",
            "forest_power",
            "ocean_power"
        ])
