import json

import pytest

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from slay_the_spire2.models import Card, Character, Encounter, Relic, RunEncounter, RunFile, RunSummary, RunSummaryCard


@pytest.mark.django_db
class TestRunFileModel:
    def test_save_populates_original_file_name_and_parsed_payload(self):
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "1711111111.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772916631, "ascension": 3, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE", "players": [{"character": "CHARACTER.IRONCLAD", "relics": [{"id": "RELIC.SPARKLING_ROUGE"}], "deck": [{"id": "CARD.BODYGUARD"}, {"id": "CARD.BODYGUARD"}, {"id": "CARD.STRIKE_NECROBINDER"}, {"id": "CARD.DEFEND_NECROBINDER"}]}]}',
                content_type="application/json",
            )
        )

        assert run_file.original_file_name == "1711111111.run"
        assert run_file.parsed_payload == {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916631,
            "ascension": 3,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "players": [
                {
                    "character": "CHARACTER.IRONCLAD",
                    "relics": [{"id": "RELIC.SPARKLING_ROUGE"}],
                    "deck": [
                        {"id": "CARD.BODYGUARD"},
                        {"id": "CARD.BODYGUARD"},
                        {"id": "CARD.STRIKE_NECROBINDER"},
                        {"id": "CARD.DEFEND_NECROBINDER"},
                    ],
                }
            ],
        }
        assert run_file.summary.win is True
        assert run_file.summary.abandonned is False
        assert run_file.summary.character.name == "IRONCLAD"
        assert run_file.summary.start_time == 1772916631
        assert run_file.summary.ascension == 3
        assert run_file.summary.killed_by is None
        assert run_file.summary.relics.count() == 1
        assert run_file.summary.relics.first().name == "SPARKLING ROUGE"
        assert run_file.summary.cards.count() == 3
        assert RunSummaryCard.objects.get(run_summary=run_file.summary, card__name="Bodyguard").quantity == 2
        assert RunSummaryCard.objects.get(run_summary=run_file.summary, card__name="Strike").quantity == 1
        assert RunSummaryCard.objects.get(run_summary=run_file.summary, card__name="Defend").quantity == 1
        assert Character.objects.filter(name="IRONCLAD").count() == 1
        assert Relic.objects.filter(name="SPARKLING ROUGE").count() == 1
        assert Card.objects.filter(name="Bodyguard").count() == 1
        assert Card.objects.filter(name="Strike").count() == 1
        assert Card.objects.filter(name="Defend").count() == 1

    def test_save_raises_validation_error_when_file_is_not_valid_json(self):
        run_file = RunFile(
            file=SimpleUploadedFile(
                "bad.run",
                b'{"character_chosen": "WATCHER"',
                content_type="application/json",
            )
        )

        with pytest.raises(ValidationError, match="JSON valide"):
            run_file.save()

    def test_save_populates_killed_by_from_encounter(self):
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "encounter.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772916640, "ascension": 1, "killed_by_encounter": "ENCOUNTER.KNIGHTS_ELITE", "killed_by_event": "NONE.NONE"}',
                content_type="application/json",
            )
        )

        assert run_file.summary.killed_by.name == "Knights"
        assert run_file.summary.killed_by.type == Encounter.Type.ELITE

    def test_save_populates_killed_by_from_event(self):
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "event.run",
                b'{"win": false, "was_abandoned": true, "start_time": 1772916650, "ascension": 0, "killed_by_encounter": "NONE.NONE", "killed_by_event": "EVENT.ROOM_FULL_OF_CHEESE", "map_point_history": [["EVENT.A", "EVENT.B"]]}',
                content_type="application/json",
            )
        )

        assert run_file.summary.killed_by.name == "Room Full Of Cheese"
        assert run_file.summary.killed_by.type == Encounter.Type.ROOM

    def test_save_raises_validation_error_when_both_killed_by_values_are_set(self):
        run_file = RunFile(
            file=SimpleUploadedFile(
                "invalid-killed-by.run",
                b'{"win": false, "was_abandoned": false, "start_time": 1772916660, "ascension": 2, "killed_by_encounter": "ENCOUNTER.BOSS", "killed_by_event": "EVENT.SPIKES"}',
                content_type="application/json",
            )
        )

        with pytest.raises(ValidationError, match="deux differents de NONE.NONE"):
            run_file.save()

        assert RunFile.objects.count() == 0
        assert RunSummary.objects.count() == 0

    def test_save_raises_validation_error_when_players_contains_multiple_entries(self):
        run_file = RunFile(
            file=SimpleUploadedFile(
                "multiplayer.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772916670, "ascension": 0, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE", "players": [{"character": "CHARACTER.IRONCLAD"}, {"character": "CHARACTER.SILENT"}]}',
                content_type="application/json",
            )
        )

        with pytest.raises(ValidationError, match="multiplayer non geree"):
            run_file.save()

        assert RunFile.objects.count() == 0
        assert RunSummary.objects.count() == 0

    def test_save_raises_validation_error_when_deck_id_is_invalid(self):
        run_file = RunFile(
            file=SimpleUploadedFile(
                "invalid-deck.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772916680, "ascension": 0, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE", "players": [{"character": "CHARACTER.IRONCLAD", "deck": [{"id": "BODYGUARD"}]}]}',
                content_type="application/json",
            )
        )

        with pytest.raises(ValidationError, match="CARD.\\{name\\}"):
            run_file.save()

        assert RunFile.objects.count() == 0
        assert RunSummary.objects.count() == 0

    def test_save_rejects_abandoned_run_with_less_than_two_encounters(self):
        run_file = RunFile(
            file=SimpleUploadedFile(
                "short-abandoned.run",
                b'{"win": false, "was_abandoned": true, "start_time": 1772916680, "ascension": 0, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE", "map_point_history": [["EVENT.ONLY_ONE"]]}',
                content_type="application/json",
            )
        )

        with pytest.raises(ValidationError, match="abandonnee avec moins de 2 encounters"):
            run_file.save()

        assert RunFile.objects.count() == 0
        assert RunSummary.objects.count() == 0

    def test_save_creates_run_encounters_from_map_point_history(self):
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "encounters.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772916681, "ascension": 0, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE", "map_point_history": [["ENCOUNTER.CULTIST_MONSTER", "EVENT.ROOM_TEST"], ["REST_SITE.CAMPFIRE"], ["ENCOUNTER.BOSS_BOSS"]]}',
                content_type="application/json",
            )
        )

        run_encounters = list(RunEncounter.objects.filter(run_summary=run_file.summary).order_by("act", "floor"))

        assert len(run_encounters) == 4
        assert [(entry.act, entry.floor) for entry in run_encounters] == [(0, 0), (0, 1), (1, 0), (2, 0)]
        assert all(entry.damage_taken == 0 for entry in run_encounters)
        assert run_encounters[0].encounter.name == "ENCOUNTER.CULTIST_MONSTER"
        assert run_encounters[1].encounter.name == "EVENT.ROOM_TEST"
        assert run_encounters[2].encounter.name == "REST_SITE.CAMPFIRE"
        assert run_encounters[3].encounter.name == "ENCOUNTER.BOSS_BOSS"

    def test_save_raises_validation_error_when_map_point_history_item_is_not_a_string(self):
        run_file = RunFile(
            file=SimpleUploadedFile(
                "invalid-map-point-history.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772916682, "ascension": 0, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE", "map_point_history": [["ENCOUNTER.CULTIST_MONSTER", 42]]}',
                content_type="application/json",
            )
        )

        with pytest.raises(ValidationError, match="map_point_history"):
            run_file.save()

        assert RunFile.objects.count() == 0
        assert RunSummary.objects.count() == 0

    def test_save_converts_ancient_map_point_history_item_to_run_encounter(self):
        map_point_item = {
            "map_point_type": "ancient",
            "player_stats": [
                {
                    "damage_taken": 7,
                }
            ],
            "rooms": [
                {
                    "model_id": "EVENT.NEOW",
                    "room_type": "event",
                    "turns_taken": 0,
                }
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916683,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "ancient-map-point.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        run_encounter = RunEncounter.objects.get(run_summary=run_file.summary)
        assert run_encounter.act == 0
        assert run_encounter.floor == 0
        assert run_encounter.damage_taken == 7
        assert run_encounter.encounter.type == Encounter.Type.ANCIENT
        assert run_encounter.encounter.name == "Neow"

    def test_save_raises_validation_error_when_ancient_rooms_contains_multiple_items(self):
        map_point_item = {
            "map_point_type": "ancient",
            "player_stats": [
                {
                    "damage_taken": 0,
                }
            ],
            "rooms": [
                {"model_id": "EVENT.NEOW"},
                {"model_id": "EVENT.NEOW_2"},
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916684,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile(
            file=SimpleUploadedFile(
                "invalid-ancient-rooms.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        with pytest.raises(ValidationError, match="rooms"):
            run_file.save()

    def test_save_raises_validation_error_when_ancient_player_stats_contains_multiple_items(self):
        map_point_item = {
            "map_point_type": "ancient",
            "player_stats": [
                {"damage_taken": 0},
                {"damage_taken": 1},
            ],
            "rooms": [
                {"model_id": "EVENT.NEOW"},
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916685,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile(
            file=SimpleUploadedFile(
                "invalid-ancient-player-stats.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        with pytest.raises(ValidationError, match="player_stats"):
            run_file.save()

    def test_save_converts_monster_map_point_history_item_to_run_encounter(self):
        map_point_item = {
            "map_point_type": "monster",
            "player_stats": [
                {
                    "damage_taken": 8,
                }
            ],
            "rooms": [
                {
                    "model_id": "ENCOUNTER.GLOBE_HEAD_NORMAL",
                    "monster_ids": ["MONSTER.GLOBE_HEAD"],
                    "room_type": "monster",
                    "turns_taken": 4,
                }
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916686,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "monster-map-point.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        run_encounter = RunEncounter.objects.get(run_summary=run_file.summary)
        assert run_encounter.act == 0
        assert run_encounter.floor == 0
        assert run_encounter.damage_taken == 8
        assert run_encounter.encounter.type == Encounter.Type.MONSTER
        assert run_encounter.encounter.name == "Globe Head"

    def test_save_converts_unknown_map_point_with_monster_room_to_monster_encounter(self):
        map_point_item = {
            "map_point_type": "unknown",
            "player_stats": [
                {
                    "damage_taken": 0,
                }
            ],
            "rooms": [
                {
                    "model_id": "ENCOUNTER.SHRINKER_BEETLE_WEAK",
                    "monster_ids": ["MONSTER.SHRINKER_BEETLE"],
                    "room_type": "monster",
                    "turns_taken": 3,
                }
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916694,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "unknown-monster-map-point.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        run_encounter = RunEncounter.objects.get(run_summary=run_file.summary)
        assert run_encounter.act == 0
        assert run_encounter.floor == 0
        assert run_encounter.damage_taken == 0
        assert run_encounter.encounter.type == Encounter.Type.MONSTER
        assert run_encounter.encounter.name == "Shrinker Beetle"

    def test_save_converts_elite_map_point_history_item_to_run_encounter(self):
        map_point_item = {
            "map_point_type": "elite",
            "player_stats": [
                {
                    "damage_taken": 32,
                }
            ],
            "rooms": [
                {
                    "model_id": "ENCOUNTER.MECHA_KNIGHT_ELITE",
                    "monster_ids": ["MONSTER.MECHA_KNIGHT"],
                    "room_type": "elite",
                    "turns_taken": 5,
                }
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916687,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "elite-map-point.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        run_encounter = RunEncounter.objects.get(run_summary=run_file.summary)
        assert run_encounter.act == 0
        assert run_encounter.floor == 0
        assert run_encounter.damage_taken == 32
        assert run_encounter.encounter.type == Encounter.Type.ELITE
        assert run_encounter.encounter.name == "Mecha Knight"

    def test_save_converts_shop_map_point_history_item_to_run_encounter(self):
        map_point_item = {
            "map_point_type": "shop",
            "player_stats": [
                {
                    "damage_taken": 0,
                }
            ],
            "rooms": [
                {
                    "room_type": "shop",
                    "turns_taken": 0,
                }
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916688,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "shop-map-point.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        run_encounter = RunEncounter.objects.get(run_summary=run_file.summary)
        assert run_encounter.act == 0
        assert run_encounter.floor == 0
        assert run_encounter.damage_taken == 0
        assert run_encounter.encounter.type == Encounter.Type.SHOP
        assert run_encounter.encounter.name == "Shop"

    def test_save_converts_unknown_map_point_with_shop_room_to_shop_encounter(self):
        map_point_item = {
            "map_point_type": "unknown",
            "player_stats": [
                {
                    "damage_taken": 0,
                }
            ],
            "rooms": [
                {
                    "room_type": "shop",
                    "turns_taken": 0,
                }
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916693,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "unknown-shop-map-point.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        run_encounter = RunEncounter.objects.get(run_summary=run_file.summary)
        assert run_encounter.act == 0
        assert run_encounter.floor == 0
        assert run_encounter.damage_taken == 0
        assert run_encounter.encounter.type == Encounter.Type.SHOP
        assert run_encounter.encounter.name == "Shop"

    def test_save_converts_treasure_map_point_history_item_to_run_encounter(self):
        map_point_item = {
            "map_point_type": "treasure",
            "player_stats": [
                {
                    "damage_taken": 0,
                }
            ],
            "rooms": [
                {
                    "room_type": "treasure",
                    "turns_taken": 0,
                }
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916689,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "treasure-map-point.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        run_encounter = RunEncounter.objects.get(run_summary=run_file.summary)
        assert run_encounter.act == 0
        assert run_encounter.floor == 0
        assert run_encounter.damage_taken == 0
        assert run_encounter.encounter.type == Encounter.Type.TREASURE
        assert run_encounter.encounter.name == "Treasure"

    def test_save_converts_unknown_map_point_with_treasure_room_to_treasure_encounter(self):
        map_point_item = {
            "map_point_type": "unknown",
            "player_stats": [
                {
                    "damage_taken": 0,
                }
            ],
            "rooms": [
                {
                    "room_type": "treasure",
                    "turns_taken": 0,
                }
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916695,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "unknown-treasure-map-point.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        run_encounter = RunEncounter.objects.get(run_summary=run_file.summary)
        assert run_encounter.act == 0
        assert run_encounter.floor == 0
        assert run_encounter.damage_taken == 0
        assert run_encounter.encounter.type == Encounter.Type.TREASURE
        assert run_encounter.encounter.name == "Treasure"

    def test_save_converts_rest_site_map_point_history_item_to_run_encounter(self):
        map_point_item = {
            "map_point_type": "rest_site",
            "player_stats": [
                {
                    "damage_taken": 0,
                }
            ],
            "rooms": [
                {
                    "room_type": "rest_site",
                    "turns_taken": 0,
                }
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916690,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "rest-site-map-point.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        run_encounter = RunEncounter.objects.get(run_summary=run_file.summary)
        assert run_encounter.act == 0
        assert run_encounter.floor == 0
        assert run_encounter.damage_taken == 0
        assert run_encounter.encounter.type == Encounter.Type.REST_SITE
        assert run_encounter.encounter.name == "Rest Site"

    def test_save_converts_unknown_map_point_with_event_room_to_room_encounter(self):
        map_point_item = {
            "map_point_type": "unknown",
            "player_stats": [
                {
                    "damage_taken": 0,
                }
            ],
            "rooms": [
                {
                    "model_id": "EVENT.AROMA_OF_CHAOS",
                    "room_type": "event",
                    "turns_taken": 0,
                }
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916691,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "unknown-event-map-point.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        run_encounter = RunEncounter.objects.get(run_summary=run_file.summary)
        assert run_encounter.act == 0
        assert run_encounter.floor == 0
        assert run_encounter.damage_taken == 0
        assert run_encounter.encounter.type == Encounter.Type.ROOM
        assert run_encounter.encounter.name == "Aroma Of Chaos"

    def test_save_converts_boss_map_point_history_item_to_run_encounter(self):
        map_point_item = {
            "map_point_type": "boss",
            "player_stats": [
                {
                    "damage_taken": 40,
                }
            ],
            "rooms": [
                {
                    "model_id": "ENCOUNTER.QUEEN_BOSS",
                    "monster_ids": [
                        "MONSTER.TORCH_HEAD_AMALGAM",
                        "MONSTER.QUEEN",
                    ],
                    "room_type": "boss",
                    "turns_taken": 7,
                }
            ],
        }
        payload = {
            "win": True,
            "was_abandoned": False,
            "start_time": 1772916692,
            "ascension": 0,
            "killed_by_encounter": "NONE.NONE",
            "killed_by_event": "NONE.NONE",
            "map_point_history": [[map_point_item]],
        }
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "boss-map-point.run",
                json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )
        )

        run_encounter = RunEncounter.objects.get(run_summary=run_file.summary)
        assert run_encounter.act == 0
        assert run_encounter.floor == 0
        assert run_encounter.damage_taken == 40
        assert run_encounter.encounter.type == Encounter.Type.BOSS
        assert run_encounter.encounter.name == "Queen"
