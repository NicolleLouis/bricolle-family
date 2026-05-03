from collections import Counter
import logging

from slay_the_spire2.models.card import Card
from slay_the_spire2.models.character import Character
from slay_the_spire2.models.encounter import Encounter
from slay_the_spire2.models.relic import Relic
from slay_the_spire2.models.run_encounter import RunEncounter
from slay_the_spire2.models.run_summary import RunSummary
from slay_the_spire2.models.run_summary_card import RunSummaryCard

logger = logging.getLogger(__name__)


class RunSummaryBuilderService:
    _NONE_VALUE = "NONE.NONE"

    def upsert_from_run_file(self, run_file) -> RunSummary:
        payload = run_file.parsed_payload
        defaults = {
            "win": self._read_boolean(payload, "win"),
            "abandonned": self._read_boolean(payload, "was_abandoned"),
            "character": self._extract_character(payload),
            "start_time": self._read_integer(payload, "start_time"),
            "ascension": self._read_integer(payload, "ascension"),
            "killed_by": self._extract_killed_by(payload),
        }
        summary, _ = RunSummary.objects.update_or_create(run_file=run_file, defaults=defaults)
        summary.relics.set(self._extract_relics(payload))
        self._replace_deck_entries(summary, payload)
        self._replace_run_encounters(summary, payload)
        return summary

    def _read_boolean(self, payload: dict, key: str) -> bool:
        value = payload.get(key)
        if not isinstance(value, bool):
            raise ValueError(f"Le champ '{key}' doit etre un booleen.")
        return value

    def _read_integer(self, payload: dict, key: str) -> int:
        value = payload.get(key)
        if not isinstance(value, int):
            raise ValueError(f"Le champ '{key}' doit etre un entier.")
        return value

    def _extract_killed_by(self, payload: dict) -> Encounter | None:
        killed_by_encounter = self._normalize_killed_by_value(payload.get("killed_by_encounter"), "killed_by_encounter")
        killed_by_event = self._normalize_killed_by_value(payload.get("killed_by_event"), "killed_by_event")

        if killed_by_encounter == self._NONE_VALUE and killed_by_event == self._NONE_VALUE:
            return None
        if killed_by_encounter != self._NONE_VALUE and killed_by_event == self._NONE_VALUE:
            return self._build_encounter_from_killed_by_value(killed_by_encounter)
        if killed_by_encounter == self._NONE_VALUE and killed_by_event != self._NONE_VALUE:
            return self._build_encounter_from_killed_by_value(killed_by_event)

        raise ValueError(
            "Les champs 'killed_by_encounter' et 'killed_by_event' ne peuvent pas etre tous les deux differents de NONE.NONE."
        )

    def _normalize_killed_by_value(self, value, field_name: str) -> str:
        if value is None:
            return self._NONE_VALUE
        if not isinstance(value, str):
            raise ValueError(f"Le champ '{field_name}' doit etre une chaine de caracteres.")
        return value

    def _build_encounter_from_killed_by_value(self, raw_value: str) -> Encounter:
        if raw_value.startswith("ENCOUNTER."):
            return self._build_encounter_from_encounter_value(raw_value)
        if raw_value.startswith("EVENT."):
            return self._build_encounter_from_event_value(raw_value)

        raise ValueError("Le champ killed_by doit commencer par ENCOUNTER. ou EVENT.")

    def _build_encounter_from_encounter_value(self, raw_value: str) -> Encounter:
        payload = raw_value[len("ENCOUNTER."):]
        if "_" not in payload:
            raise ValueError("Le champ ENCOUNTER doit avoir le format ENCOUNTER.{name}_{type}.")

        raw_name, raw_type = payload.rsplit("_", 1)
        encounter_type = self._convert_encounter_type(raw_type)
        encounter_name = self._normalize_encounter_name(raw_name)
        encounter, _ = Encounter.objects.get_or_create(type=encounter_type, name=encounter_name)
        return encounter

    def _build_encounter_from_event_value(self, raw_value: str) -> Encounter:
        payload = raw_value[len("EVENT."):]
        if "_" not in payload:
            raise ValueError("Le champ EVENT doit avoir le format EVENT.{type}_{name}.")

        raw_type, raw_name = payload.split("_", 1)
        encounter_type = self._convert_event_type(raw_type)
        if not raw_name:
            raise ValueError("Le nom de l'event est vide.")
        encounter_name = self._normalize_encounter_name(payload)
        encounter, _ = Encounter.objects.get_or_create(type=encounter_type, name=encounter_name)
        return encounter

    def _convert_encounter_type(self, raw_type: str) -> str:
        converted_types = {
            "NORMAL": Encounter.Type.MONSTER,
            "ELITE": Encounter.Type.ELITE,
            "BOSS": Encounter.Type.BOSS,
        }
        if raw_type not in converted_types:
            raise ValueError(f"Type de killed_by non gere pour le moment: {raw_type}.")
        return converted_types[raw_type]

    def _normalize_encounter_name(self, raw_name: str) -> str:
        if not raw_name:
            raise ValueError("Le nom de l'encounter est vide.")
        return raw_name.replace("_", " ").title()

    def _convert_event_type(self, raw_type: str) -> str:
        converted_types = {
            "ROOM": Encounter.Type.ROOM,
        }
        if raw_type not in converted_types:
            raise ValueError(f"Type d'event killed_by non gere pour le moment: {raw_type}.")
        return converted_types[raw_type]

    def _extract_character(self, payload: dict) -> Character | None:
        first_player = self._extract_first_player(payload, max_players=1)
        if first_player is None:
            return None

        raw_character = first_player.get("character")
        if raw_character is None:
            return None
        if not isinstance(raw_character, str):
            raise ValueError("Le champ 'players[0].character' doit etre une chaine de caracteres.")

        prefix = "CHARACTER."
        if not raw_character.startswith(prefix) or len(raw_character) <= len(prefix):
            raise ValueError("Le champ 'players[0].character' doit avoir le format CHARACTER.{character_name}.")

        character_name = raw_character[len(prefix):]
        character, _ = Character.objects.get_or_create(name=character_name)
        return character

    def _extract_relics(self, payload: dict) -> list[Relic]:
        first_player = self._extract_first_player(payload, max_players=2)
        if first_player is None:
            return []

        relics = first_player.get("relics", [])
        if not isinstance(relics, list):
            raise ValueError("Le champ 'players[0].relics' doit etre une liste.")

        parsed_relics = []
        for relic_data in relics:
            if not isinstance(relic_data, dict):
                raise ValueError("Chaque relic de 'players[0].relics' doit etre un objet.")
            raw_relic_id = relic_data.get("id")
            if not isinstance(raw_relic_id, str):
                raise ValueError("Le champ 'players[0].relics[].id' doit etre une chaine de caracteres.")

            relic_name = self._parse_relic_name(raw_relic_id)
            relic, _ = Relic.objects.get_or_create(name=relic_name)
            parsed_relics.append(relic)

        return parsed_relics

    def _parse_relic_name(self, raw_relic_id: str) -> str:
        prefix = "RELIC."
        if not raw_relic_id.startswith(prefix) or len(raw_relic_id) <= len(prefix):
            raise ValueError("Le champ 'players[0].relics[].id' doit avoir le format RELIC.{name}.")
        return raw_relic_id[len(prefix):].replace("_", " ")

    def _replace_deck_entries(self, summary: RunSummary, payload: dict) -> None:
        parsed_cards = self._extract_cards_with_quantities(payload)
        summary.deck_entries.all().delete()
        RunSummaryCard.objects.bulk_create(
            [
                RunSummaryCard(
                    run_summary=summary,
                    card=card,
                    quantity=quantity,
                )
                for card, quantity in parsed_cards
            ]
        )

    def _extract_cards_with_quantities(self, payload: dict) -> list[tuple[Card, int]]:
        first_player = self._extract_first_player(payload, max_players=2)
        if first_player is None:
            return []

        deck = first_player.get("deck", [])
        if not isinstance(deck, list):
            raise ValueError("Le champ 'players[0].deck' doit etre une liste.")

        card_name_counter = Counter()
        for card_data in deck:
            if not isinstance(card_data, dict):
                raise ValueError("Chaque carte de 'players[0].deck' doit etre un objet.")
            raw_card_id = card_data.get("id")
            if not isinstance(raw_card_id, str):
                raise ValueError("Le champ 'players[0].deck[].id' doit etre une chaine de caracteres.")

            card_name = self._parse_card_name(raw_card_id)
            card_name_counter[card_name] += 1

        parsed_cards = []
        for card_name, quantity in card_name_counter.items():
            card, _ = Card.objects.get_or_create(name=card_name)
            parsed_cards.append((card, quantity))

        return parsed_cards

    def _parse_card_name(self, raw_card_id: str) -> str:
        prefix = "CARD."
        if not raw_card_id.startswith(prefix) or len(raw_card_id) <= len(prefix):
            raise ValueError("Le champ 'players[0].deck[].id' doit avoir le format CARD.{name}.")

        raw_card_name = raw_card_id[len(prefix):]
        if raw_card_name.startswith("STRIKE_") or raw_card_name.startswith("STRIKE-"):
            return "Strike"
        if raw_card_name.startswith("DEFEND_") or raw_card_name.startswith("DEFEND-"):
            return "Defend"

        normalized_card_name = raw_card_name.replace("_", " ").replace("-", " ").strip()
        return normalized_card_name.title()

    def _extract_first_player(self, payload: dict, max_players: int) -> dict | None:
        players = payload.get("players")
        if players is None:
            return None
        if not isinstance(players, list):
            raise ValueError("Le champ 'players' doit etre une liste.")
        if len(players) == 0:
            return None
        if len(players) > max_players:
            raise ValueError("Partie multiplayer non geree.")

        first_player = players[0]
        if not isinstance(first_player, dict):
            raise ValueError("Le premier element de 'players' doit etre un objet.")
        return first_player

    def _replace_run_encounters(self, summary: RunSummary, payload: dict) -> None:
        map_point_history = payload.get("map_point_history")
        if map_point_history is None:
            summary.encounters.all().delete()
            return
        if not isinstance(map_point_history, list):
            raise ValueError("Le champ 'map_point_history' doit etre une liste.")

        parsed_entries: list[RunEncounter] = []
        for act_index, act_entries in enumerate(map_point_history):
            if act_index > RunEncounter.Act.ACT_3:
                raise ValueError("Le champ 'map_point_history' ne peut pas contenir plus de 3 acts.")
            if not isinstance(act_entries, list):
                raise ValueError("Chaque element de 'map_point_history' doit etre une liste.")

            for floor_index, map_point in enumerate(act_entries):
                try:
                    encounter, damage_taken = self._parse_map_point_history_item(map_point)
                except Exception:
                    logger.exception(
                        "Erreur de parsing map_point_history (act=%s, floor=%s, map_point=%s)",
                        act_index,
                        floor_index,
                        map_point,
                    )
                    raise
                parsed_entries.append(
                    RunEncounter(
                        run_summary=summary,
                        encounter=encounter,
                        act=act_index,
                        floor=floor_index,
                        damage_taken=damage_taken,
                    )
                )

        summary.encounters.all().delete()
        RunEncounter.objects.bulk_create(parsed_entries)

    def _parse_map_point_history_item(self, map_point) -> tuple[Encounter, int]:
        if isinstance(map_point, str):
            return self._parse_string_map_point_history_item(map_point)
        if isinstance(map_point, dict):
            return self._parse_object_map_point_history_item(map_point)
        raise ValueError("Chaque item de 'map_point_history' doit etre une chaine ou un objet.")

    def _parse_string_map_point_history_item(self, map_point: str) -> tuple[Encounter, int]:
        if not map_point:
            raise ValueError("Les items de 'map_point_history' ne peuvent pas etre vides.")

        encounter, _ = Encounter.objects.get_or_create(
            type=Encounter.Type.ROOM,
            name=map_point,
        )
        return encounter, 0

    def _parse_object_map_point_history_item(self, map_point: dict) -> tuple[Encounter, int]:
        map_point_type = map_point.get("map_point_type")
        if not isinstance(map_point_type, str):
            raise ValueError("Le champ 'map_point_type' de map_point_history doit etre une chaine de caracteres.")
        if self._has_room_type(map_point, "shop"):
            encounter_type, encounter_name = self._extract_shop_encounter_from_rooms(map_point)
        elif self._has_room_type(map_point, "monster"):
            encounter_type, encounter_name = self._extract_monster_encounter_from_rooms(map_point)
        elif self._has_room_type(map_point, "treasure"):
            encounter_type, encounter_name = self._extract_treasure_encounter_from_rooms(map_point)
        elif map_point_type == Encounter.Type.ANCIENT:
            encounter_type = Encounter.Type.ANCIENT
            encounter_name = self._extract_ancient_encounter_name_from_rooms(map_point)
        elif map_point_type == Encounter.Type.REST_SITE:
            encounter_type, encounter_name = self._extract_rest_site_encounter_from_rooms(map_point)
        elif map_point_type == Encounter.Type.ELITE:
            encounter_type, encounter_name = self._extract_elite_encounter_from_rooms(map_point)
        elif map_point_type == Encounter.Type.BOSS:
            encounter_type, encounter_name = self._extract_boss_encounter_from_rooms(map_point)
        else:
            encounter_type, encounter_name = self._extract_room_encounter_from_event_room(map_point, map_point_type)

        damage_taken = self._extract_damage_taken_from_player_stats(map_point)
        encounter, _ = Encounter.objects.get_or_create(
            type=encounter_type,
            name=encounter_name,
        )
        return encounter, damage_taken

    def _extract_ancient_encounter_name_from_rooms(self, map_point: dict) -> str:
        first_room = self._extract_room_by_type(map_point, "event")
        model_id = first_room.get("model_id")
        if not isinstance(model_id, str):
            raise ValueError("Le champ 'rooms[0].model_id' doit etre une chaine de caracteres.")
        prefix = "EVENT."
        if not model_id.startswith(prefix) or len(model_id) <= len(prefix):
            raise ValueError("Le champ 'rooms[0].model_id' doit avoir le format EVENT.{name}.")

        return self._normalize_encounter_name(model_id[len(prefix):])

    def _extract_monster_encounter_from_rooms(self, map_point: dict) -> tuple[str, str]:
        first_room = self._extract_room_by_type(map_point, "monster")

        model_id = first_room.get("model_id")
        if not isinstance(model_id, str):
            raise ValueError("Le champ 'rooms[0].model_id' doit etre une chaine de caracteres.")
        prefix = "ENCOUNTER."
        if not model_id.startswith(prefix) or len(model_id) <= len(prefix):
            raise ValueError("Le champ 'rooms[0].model_id' doit avoir le format ENCOUNTER.{name}.")

        raw_name = model_id[len(prefix):]
        for suffix in ("_NORMAL", "_WEAK"):
            if raw_name.endswith(suffix):
                raw_name = raw_name[: -len(suffix)]
                break
        if not raw_name:
            raise ValueError("Le nom de l'encounter monster est vide.")

        return Encounter.Type.MONSTER, self._normalize_encounter_name(raw_name)

    def _extract_shop_encounter_from_rooms(self, map_point: dict) -> tuple[str, str]:
        self._extract_room_by_type(map_point, "shop")
        return Encounter.Type.SHOP, "Shop"

    def _extract_treasure_encounter_from_rooms(self, map_point: dict) -> tuple[str, str]:
        self._extract_room_by_type(map_point, "treasure")
        return Encounter.Type.TREASURE, "Treasure"

    def _extract_rest_site_encounter_from_rooms(self, map_point: dict) -> tuple[str, str]:
        self._extract_room_by_type(map_point, "rest_site")
        return Encounter.Type.REST_SITE, "Rest Site"

    def _extract_room_encounter_from_event_room(self, map_point: dict, map_point_type: str) -> tuple[str, str]:
        if not self._has_room_type(map_point, "event"):
            raise ValueError(f"Le map_point_type '{map_point_type}' n'est pas gere pour le moment.")
        first_room = self._extract_room_by_type(map_point, "event")

        model_id = first_room.get("model_id")
        if not isinstance(model_id, str):
            raise ValueError("Le champ 'rooms[0].model_id' doit etre une chaine de caracteres.")
        prefix = "EVENT."
        if not model_id.startswith(prefix) or len(model_id) <= len(prefix):
            raise ValueError("Le champ 'rooms[0].model_id' doit avoir le format EVENT.{name}.")

        return Encounter.Type.ROOM, self._normalize_encounter_name(model_id[len(prefix):])

    def _extract_elite_encounter_from_rooms(self, map_point: dict) -> tuple[str, str]:
        first_room = self._extract_room_by_type(map_point, "elite")

        model_id = first_room.get("model_id")
        if not isinstance(model_id, str):
            raise ValueError("Le champ 'rooms[0].model_id' doit etre une chaine de caracteres.")
        prefix = "ENCOUNTER."
        if not model_id.startswith(prefix) or len(model_id) <= len(prefix):
            raise ValueError("Le champ 'rooms[0].model_id' doit avoir le format ENCOUNTER.{name}.")

        raw_name = model_id[len(prefix):]
        suffix = "_ELITE"
        if raw_name.endswith(suffix):
            raw_name = raw_name[: -len(suffix)]
        if not raw_name:
            raise ValueError("Le nom de l'encounter elite est vide.")

        return Encounter.Type.ELITE, self._normalize_encounter_name(raw_name)

    def _extract_boss_encounter_from_rooms(self, map_point: dict) -> tuple[str, str]:
        first_room = self._extract_room_by_type(map_point, "boss")

        model_id = first_room.get("model_id")
        if not isinstance(model_id, str):
            raise ValueError("Le champ 'rooms[0].model_id' doit etre une chaine de caracteres.")
        prefix = "ENCOUNTER."
        if not model_id.startswith(prefix) or len(model_id) <= len(prefix):
            raise ValueError("Le champ 'rooms[0].model_id' doit avoir le format ENCOUNTER.{name}.")

        raw_name = model_id[len(prefix):]
        suffix = "_BOSS"
        if raw_name.endswith(suffix):
            raw_name = raw_name[: -len(suffix)]
        if not raw_name:
            raise ValueError("Le nom de l'encounter boss est vide.")

        return Encounter.Type.BOSS, self._normalize_encounter_name(raw_name)

    def _has_room_type(self, map_point: dict, room_type: str) -> bool:
        rooms = self._extract_rooms(map_point)
        return any(self._room_matches_type(room, room_type) for room in rooms)

    def _extract_room_by_type(self, map_point: dict, room_type: str) -> dict:
        rooms = self._extract_rooms(map_point)
        matching_rooms = [room for room in rooms if self._room_matches_type(room, room_type)]
        if len(matching_rooms) == 0:
            raise ValueError(f"Le champ 'rooms' de map_point_history doit contenir une room de type '{room_type}'.")
        if len(matching_rooms) > 1:
            raise ValueError(f"Le champ 'rooms' de map_point_history contient plusieurs rooms de type '{room_type}'.")
        return matching_rooms[0]

    def _room_matches_type(self, room: dict, room_type: str) -> bool:
        explicit_room_type = room.get("room_type")
        if explicit_room_type == room_type:
            return True
        if room_type == "event":
            model_id = room.get("model_id")
            return isinstance(model_id, str) and model_id.startswith("EVENT.")
        return False

    def _extract_rooms(self, map_point: dict) -> list[dict]:
        rooms = map_point.get("rooms")
        if not isinstance(rooms, list):
            raise ValueError("Le champ 'rooms' de map_point_history doit etre une liste.")
        if len(rooms) == 0:
            raise ValueError("Le champ 'rooms' de map_point_history doit contenir un element.")

        for room in rooms:
            if not isinstance(room, dict):
                raise ValueError("Chaque element de 'rooms' doit etre un objet.")
        return rooms

    def _extract_damage_taken_from_player_stats(self, map_point: dict) -> int:
        player_stats = map_point.get("player_stats")
        if not isinstance(player_stats, list):
            raise ValueError("Le champ 'player_stats' de map_point_history doit etre une liste.")
        if len(player_stats) == 0:
            raise ValueError("Le champ 'player_stats' de map_point_history doit contenir un element.")
        if len(player_stats) > 1:
            raise ValueError("Le champ 'player_stats' de map_point_history ne peut pas contenir plus d'un element.")

        first_player_stat = player_stats[0]
        if not isinstance(first_player_stat, dict):
            raise ValueError("Le premier element de 'player_stats' doit etre un objet.")

        damage_taken = first_player_stat.get("damage_taken")
        if not isinstance(damage_taken, int):
            raise ValueError("Le champ 'player_stats[0].damage_taken' doit etre un entier.")
        return damage_taken
