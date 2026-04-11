import pytest

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from slay_the_spire2.models import Character, Encounter, Relic, RunFile, RunSummary


@pytest.mark.django_db
class TestRunFileModel:
    def test_save_populates_original_file_name_and_parsed_payload(self):
        run_file = RunFile.objects.create(
            file=SimpleUploadedFile(
                "1711111111.run",
                b'{"win": true, "was_abandoned": false, "start_time": 1772916631, "ascension": 3, "killed_by_encounter": "NONE.NONE", "killed_by_event": "NONE.NONE", "players": [{"character": "CHARACTER.IRONCLAD", "relics": [{"id": "RELIC.SPARKLING_ROUGE"}]}]}',
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
            "players": [{"character": "CHARACTER.IRONCLAD", "relics": [{"id": "RELIC.SPARKLING_ROUGE"}]}],
        }
        assert run_file.summary.win is True
        assert run_file.summary.abandonned is False
        assert run_file.summary.character.name == "IRONCLAD"
        assert run_file.summary.start_time == 1772916631
        assert run_file.summary.ascension == 3
        assert run_file.summary.killed_by is None
        assert run_file.summary.relics.count() == 1
        assert run_file.summary.relics.first().name == "SPARKLING ROUGE"
        assert Character.objects.filter(name="IRONCLAD").count() == 1
        assert Relic.objects.filter(name="SPARKLING ROUGE").count() == 1

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
                b'{"win": false, "was_abandoned": true, "start_time": 1772916650, "ascension": 0, "killed_by_encounter": "NONE.NONE", "killed_by_event": "EVENT.ROOM_FULL_OF_CHEESE"}',
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
