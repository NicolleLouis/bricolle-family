from altered.constants.altered_website import AlteredWebsiteConstant
from altered.models import Deck, DeckVersion
import requests


class AlteredFetchDeckDataService:
    TIMEOUT = 30

    def __init__(self, deck: Deck):
        self.deck = deck

    def handle(self):
        card_indexes = self.get_card_list()
        description = self.transform_cards_to_str(card_indexes)
        latest_version = self.deck_latest_version()
        if latest_version.content is None:
            latest_version.content = description
            latest_version.save()
            return
        if latest_version.content == description:
            return
        self.generate_new_version(latest_version, description)

    def generate_new_version(self, latest_version, description):
        DeckVersion.objects.create(
            deck=self.deck,
            version_number=latest_version.version_number+1,
            content=description
        )


    def deck_url(self):
        return f"{AlteredWebsiteConstant.BASE_URL}/deck_user_lists/{self.deck.altered_id}"

    def get_card_list(self):
        try:
            response = requests.get(self.deck_url(), timeout=self.TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error while fetching deck data : {e}")
            raise

        data = response.json()
        return data.get("cardIndexes")

    def deck_latest_version(self):
        latest_version = self.deck.versions.order_by('-created_at').first()
        if latest_version is None:
            latest_version = DeckVersion.objects.create(deck=self.deck, version_number=1)
        return latest_version

    @staticmethod
    def transform_cards_to_str(card_indexes):
        lines = []
        for key in sorted(card_indexes.keys()):
            lines.append(f'{key}: {card_indexes[key]}')
        return "\n".join(lines)
