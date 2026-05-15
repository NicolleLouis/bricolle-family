from datetime import timedelta

import pytest
from django.utils import timezone

from albion_online.constants.artifact_salvage import ARTIFACT_SALVAGE_FAMILIES
from albion_online.constants.city import City
from albion_online.constants.object_type import ObjectType
from albion_online.models import Object, ObjectTypeGroup, Price
from albion_online.services.artifact_salvage_market_summary import (
    ArtifactSalvageMarketSummaryService,
)


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


def _create_price_series(albion_object, city, sell_prices):
    now = timezone.now()
    for quality, sell_price in enumerate(sell_prices):
        Price.objects.create(
            object=albion_object,
            city=city,
            quality=quality,
            sell_price_min=sell_price,
            sell_price_min_date=now - timedelta(minutes=quality),
            buy_price_max=sell_price + 25,
            buy_price_max_date=now - timedelta(minutes=quality),
        )


@pytest.mark.django_db
class TestArtifactSalvageMarketSummaryService:
    def test_build_sections_builds_city_rows_and_threshold_colors(self):
        _get_or_create_type_group(ObjectType.ARTEFACT)
        _get_or_create_type_group(ObjectType.RUNE)

        shard_t7 = _create_object("TEST_T7_RUNE_PRICE", ObjectType.RUNE, 7)
        shard_t8 = _create_object("TEST_T8_RUNE_PRICE", ObjectType.RUNE, 8)
        artifact_t7 = _create_object(
            "TEST_T7_ARTEFACT_MAIN_SCIMITAR_MORGANA_PRICE", ObjectType.ARTEFACT, 7
        )
        artifact_t8 = _create_object(
            "TEST_T8_ARTEFACT_MAIN_SCIMITAR_MORGANA_PRICE", ObjectType.ARTEFACT, 8
        )

        _create_price_series(shard_t7, City.BRIDGEWATCH, [200, 200, 200])
        _create_price_series(shard_t8, City.BRIDGEWATCH, [300, 300, 300])
        _create_price_series(artifact_t7, City.BRIDGEWATCH, [1000, 1000, 1000])
        _create_price_series(artifact_t8, City.BRIDGEWATCH, [2600, 2600, 2600])

        service = ArtifactSalvageMarketSummaryService()
        sections = service.build_sections(City.BRIDGEWATCH)

        assert [section["key"] for section in sections] == [family["key"] for family in ARTIFACT_SALVAGE_FAMILIES]
        rune_section = sections[0]
        assert [column["label"] for column in rune_section["columns"]] == ["T7", "T8"]
        assert rune_section["base_row"]["label"] == "Rune x10"
        assert [cell["current_price"] for cell in rune_section["base_row"]["cells"]] == [2000, 3000]
        assert [cell["current_price"] for cell in rune_section["buy_order_row"]["cells"]] == [1659, 2488]

        first_row = rune_section["artifact_rows"][0]
        assert first_row["label"] == "Bloodforged Blade"
        assert first_row["cells"][0]["current_price"] == 1000
        assert first_row["cells"][0]["price_state"] == "green_strong"
        assert first_row["cells"][1]["current_price"] == 2600
        assert first_row["cells"][1]["price_state"] == "green_pale"

    def test_build_sections_keeps_missing_objects_and_prices_safe(self):
        _get_or_create_type_group(ObjectType.ARTEFACT)

        service = ArtifactSalvageMarketSummaryService()
        sections = service.build_sections(City.BRIDGEWATCH)

        soul_section = next(section for section in sections if section["key"] == "soul")
        assert len(soul_section["artifact_rows"]) == 29
        assert [cell["current_price"] for cell in soul_section["buy_order_row"]["cells"]] == [None, None]
        assert soul_section["artifact_rows"][0]["cells"][0]["current_price"] is None
        assert soul_section["artifact_rows"][0]["cells"][0]["price_state"] is None

    def test_build_buy_order_price_uses_the_documented_formula(self):
        service = ArtifactSalvageMarketSummaryService()

        assert service._build_buy_order_price(100) == 829
        assert service._build_buy_order_price(0) == 0
        assert service._build_price_state(828, 829) == "green_strong"
        assert service._build_price_state(829, 829) == "green_pale"
        assert service._build_price_state(994, 829) == "green_pale"
        assert service._build_price_state(996, 829) == "red"
