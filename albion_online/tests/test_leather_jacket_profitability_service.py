from types import SimpleNamespace

import pytest

from albion_online.constants.city import City
from albion_online.services.leather_jacket_profitability import (
    LeatherJacketProfitabilityService,
)


def _build_fake_jacket_row(
    *,
    object_name,
    notation,
    jacket_type_key,
    jacket_type_label,
    city_details,
):
    return {
        "object": SimpleNamespace(display_name=object_name, tier_enchantment_notation=notation),
        "jacket_type_key": jacket_type_key,
        "jacket_type_label": jacket_type_label,
        "city_details": city_details,
    }


@pytest.mark.django_db
class TestLeatherJacketProfitabilityService:
    def test_build_rows_filters_profitable_rows_and_sorts_by_percentage_by_default(self):
        jacket_rows = [
            _build_fake_jacket_row(
                object_name="Mercenary Jacket 4.2",
                notation="4.2",
                jacket_type_key="mercenary",
                jacket_type_label="Mercenary",
                city_details=[
                    SimpleNamespace(
                        city=City.BRIDGEWATCH,
                        label="Bridgewatch",
                        craft_margin_percent=184.1,
                        craft_margin=127,
                        craft_cost=69,
                        is_hidden=False,
                    ),
                    SimpleNamespace(
                        city=City.CAERLEON,
                        label="Caerleon",
                        craft_margin_percent=150.0,
                        craft_margin=100,
                        craft_cost=69,
                        is_hidden=True,
                    ),
                ],
            ),
            _build_fake_jacket_row(
                object_name="Hunter Jacket 4.2",
                notation="4.2",
                jacket_type_key="hunter",
                jacket_type_label="Hunter",
                city_details=[
                    SimpleNamespace(
                        city=City.BRIDGEWATCH,
                        label="Bridgewatch",
                        craft_margin_percent=42.0,
                        craft_margin=116,
                        craft_cost=276,
                        is_hidden=False,
                    )
                ],
            ),
            _build_fake_jacket_row(
                object_name="Assassin Jacket 4.2",
                notation="4.2",
                jacket_type_key="assassin",
                jacket_type_label="Assassin",
                city_details=[
                    SimpleNamespace(
                        city=City.BRIDGEWATCH,
                        label="Bridgewatch",
                        craft_margin_percent=12.0,
                        craft_margin=10,
                        craft_cost=80,
                        is_hidden=False,
                    )
                ],
            ),
        ]

        rows = LeatherJacketProfitabilityService().build_rows(
            jacket_rows,
            selected_city_filter="all",
            selected_jacket_type_filter="all",
            minimum_percentage=20.0,
            minimum_flat=None,
            sort_by="percentage",
        )

        assert [row["object_name"] for row in rows] == [
            "Mercenary Jacket",
            "Hunter Jacket",
        ]
        assert rows[0]["tier_enchantment_notation"] == "4.2"
        assert rows[0]["city_label"] == "Bridgewatch"
        assert rows[0]["craft_margin_percent"] == pytest.approx(184.05797101449275)
        assert rows[0]["craft_margin"] == 127

    def test_build_rows_can_sort_by_flat_and_filter_city_type_and_minimum_flat(self):
        jacket_rows = [
            _build_fake_jacket_row(
                object_name="Mercenary Jacket 4.2",
                notation="4.2",
                jacket_type_key="mercenary",
                jacket_type_label="Mercenary",
                city_details=[
                    SimpleNamespace(
                        city=City.BRIDGEWATCH,
                        label="Bridgewatch",
                        craft_margin_percent=184.1,
                        craft_margin=127,
                        craft_cost=69,
                        is_hidden=False,
                    ),
                    SimpleNamespace(
                        city=City.CAERLEON,
                        label="Caerleon",
                        craft_margin_percent=184.1,
                        craft_margin=127,
                        craft_cost=69,
                        is_hidden=False,
                    ),
                ],
            ),
            _build_fake_jacket_row(
                object_name="Hunter Jacket 4.2",
                notation="4.2",
                jacket_type_key="hunter",
                jacket_type_label="Hunter",
                city_details=[
                    SimpleNamespace(
                        city=City.BRIDGEWATCH,
                        label="Bridgewatch",
                        craft_margin_percent=42.0,
                        craft_margin=116,
                        craft_cost=276,
                        is_hidden=False,
                    ),
                    SimpleNamespace(
                        city=City.CAERLEON,
                        label="Caerleon",
                        craft_margin_percent=42.0,
                        craft_margin=116,
                        craft_cost=276,
                        is_hidden=False,
                    ),
                ],
            ),
        ]

        rows = LeatherJacketProfitabilityService().build_rows(
            jacket_rows,
            selected_city_filter=City.BRIDGEWATCH,
            selected_jacket_type_filter="all",
            minimum_percentage=20.0,
            minimum_flat=120,
            sort_by="flat",
        )

        assert [row["object_name"] for row in rows] == ["Mercenary Jacket"]
        assert rows[0]["city"] == City.BRIDGEWATCH
        assert rows[0]["craft_margin"] == 127
