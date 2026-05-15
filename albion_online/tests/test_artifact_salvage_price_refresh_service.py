import pytest

from albion_online.constants.object_type import ObjectType
from albion_online.models import Object, ObjectTypeGroup
from albion_online.services import artifact_salvage_price_refresh
from albion_online.services.artifact_salvage_price_refresh import ArtifactSalvagePriceRefreshService


def _get_or_create_type_group(code):
    return ObjectTypeGroup.objects.get_or_create(code=code, defaults={"name": code.title()})[0]


def _create_object(aodp_id, type_id, tier):
    return Object.objects.create(
        aodp_id=aodp_id,
        name=aodp_id,
        type_id=type_id,
        tier=tier,
        enchantment=0,
    )


@pytest.mark.django_db
class TestArtifactSalvagePriceRefreshService:
    def test_refresh_prices_fetches_one_batch_per_family(self, monkeypatch):
        fake_families = (
            {
                "key": "rune",
                "label": "Rune",
                "shard_aodp_id_fragment": "TEST_RUNE_SHARD_FRAGMENT",
                "artifacts": (
                    {
                        "label": "Rune Artifact",
                        "aodp_id_fragment": "TEST_RUNE_ARTIFACT_FRAGMENT",
                    },
                ),
            },
            {
                "key": "soul",
                "label": "Soul",
                "shard_aodp_id_fragment": "TEST_SOUL_SHARD_FRAGMENT",
                "artifacts": (
                    {
                        "label": "Soul Artifact",
                        "aodp_id_fragment": "TEST_SOUL_ARTIFACT_FRAGMENT",
                    },
                ),
            },
            {
                "key": "relic",
                "label": "Relic",
                "shard_aodp_id_fragment": "TEST_RELIC_SHARD_FRAGMENT",
                "artifacts": (
                    {
                        "label": "Relic Artifact",
                        "aodp_id_fragment": "TEST_RELIC_ARTIFACT_FRAGMENT",
                    },
                ),
            },
            {
                "key": "avalonian",
                "label": "Avalonian",
                "shard_aodp_id_fragment": "TEST_AVALONIAN_SHARD_FRAGMENT",
                "artifacts": (
                    {
                        "label": "Avalonian Artifact",
                        "aodp_id_fragment": "TEST_AVALONIAN_ARTIFACT_FRAGMENT",
                    },
                ),
            },
        )
        monkeypatch.setattr(artifact_salvage_price_refresh, "ARTIFACT_SALVAGE_FAMILIES", fake_families)

        _get_or_create_type_group(ObjectType.ARTEFACT)
        _get_or_create_type_group(ObjectType.RUNE)
        _get_or_create_type_group(ObjectType.SOUL)
        _get_or_create_type_group(ObjectType.RELIC)
        _get_or_create_type_group(ObjectType.SHARD)

        rune_shard = _create_object("TEST_RUNE_SHARD_FRAGMENT_T6", ObjectType.RUNE, 6)
        rune_artifact = _create_object("TEST_RUNE_ARTIFACT_FRAGMENT_T6", ObjectType.ARTEFACT, 6)
        soul_shard = _create_object("TEST_SOUL_SHARD_FRAGMENT_T6", ObjectType.SOUL, 6)
        soul_artifact = _create_object("TEST_SOUL_ARTIFACT_FRAGMENT_T6", ObjectType.ARTEFACT, 6)
        relic_shard = _create_object("TEST_RELIC_SHARD_FRAGMENT_T6", ObjectType.RELIC, 6)
        relic_artifact = _create_object("TEST_RELIC_ARTIFACT_FRAGMENT_T6", ObjectType.ARTEFACT, 6)
        avalonian_shard = _create_object("TEST_AVALONIAN_SHARD_FRAGMENT_T6", ObjectType.SHARD, 6)
        avalonian_artifact = _create_object(
            "TEST_AVALONIAN_ARTIFACT_FRAGMENT_T6", ObjectType.ARTEFACT, 6
        )

        class FakeFetcher:
            def __init__(self):
                self.requested_objects_batches = []

            def fetch_current_prices(self, objects, locations=None, qualities=None):
                batch = list(objects)
                self.requested_objects_batches.append([albion_object.aodp_id for albion_object in batch])
                return [object() for _ in batch]

        fetcher = FakeFetcher()
        service = ArtifactSalvagePriceRefreshService(fetcher=fetcher)

        created_prices = service.refresh_prices()

        assert fetcher.requested_objects_batches == [
            [rune_artifact.aodp_id, rune_shard.aodp_id],
            [soul_artifact.aodp_id, soul_shard.aodp_id],
            [relic_artifact.aodp_id, relic_shard.aodp_id],
            [avalonian_artifact.aodp_id, avalonian_shard.aodp_id],
        ]
        assert created_prices and len(created_prices) == 8

    def test_describe_refresh_targets_returns_the_flat_item_ids_and_family_breakdown(self, monkeypatch):
        fake_families = (
            {
                "key": "rune",
                "label": "Rune",
                "shard_aodp_id_fragment": "TEST_RUNE_SHARD_FRAGMENT",
                "artifacts": (
                    {
                        "label": "Rune Artifact",
                        "aodp_id_fragment": "TEST_RUNE_ARTIFACT_FRAGMENT",
                    },
                ),
            },
            {
                "key": "soul",
                "label": "Soul",
                "shard_aodp_id_fragment": "TEST_SOUL_SHARD_FRAGMENT",
                "artifacts": (
                    {
                        "label": "Soul Artifact",
                        "aodp_id_fragment": "TEST_SOUL_ARTIFACT_FRAGMENT",
                    },
                ),
            },
        )
        monkeypatch.setattr(artifact_salvage_price_refresh, "ARTIFACT_SALVAGE_FAMILIES", fake_families)

        _get_or_create_type_group(ObjectType.ARTEFACT)
        _get_or_create_type_group(ObjectType.RUNE)
        _get_or_create_type_group(ObjectType.SOUL)

        rune_shard = _create_object("TEST_RUNE_SHARD_FRAGMENT_T6", ObjectType.RUNE, 6)
        rune_artifact = _create_object("TEST_RUNE_ARTIFACT_FRAGMENT_T6", ObjectType.ARTEFACT, 6)
        soul_shard = _create_object("TEST_SOUL_SHARD_FRAGMENT_T6", ObjectType.SOUL, 6)
        soul_artifact = _create_object("TEST_SOUL_ARTIFACT_FRAGMENT_T6", ObjectType.ARTEFACT, 6)

        service = ArtifactSalvagePriceRefreshService()

        description = service.describe_refresh_targets()

        assert description["batch_count"] == 2
        assert description["count"] == 4
        assert set(description["item_ids"]) == {
            rune_shard.aodp_id,
            rune_artifact.aodp_id,
            soul_shard.aodp_id,
            soul_artifact.aodp_id,
        }
        assert description["families"] == [
            {
                "key": "rune",
                "label": "Rune",
                "shard_aodp_id_fragment": "TEST_RUNE_SHARD_FRAGMENT",
                "item_ids": [rune_artifact.aodp_id, rune_shard.aodp_id],
                "count": 2,
            },
            {
                "key": "soul",
                "label": "Soul",
                "shard_aodp_id_fragment": "TEST_SOUL_SHARD_FRAGMENT",
                "item_ids": [soul_artifact.aodp_id, soul_shard.aodp_id],
                "count": 2,
            },
        ]
