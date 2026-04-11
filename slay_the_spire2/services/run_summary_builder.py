from slay_the_spire2.models.character import Character
from slay_the_spire2.models.encounter import Encounter
from slay_the_spire2.models.relic import Relic
from slay_the_spire2.models.run_summary import RunSummary


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
