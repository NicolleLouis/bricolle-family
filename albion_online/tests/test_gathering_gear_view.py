from importlib import import_module
from datetime import timedelta
import re

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from albion_online.constants.city import City
from albion_online.constants.object_type import ObjectType
from albion_online.models import (
    CraftProfitabilityDone,
    Object,
    Price,
    PriceRefreshJob,
    Recipe,
    RecipeInput,
)


def _create_ore_gathering_gear_sample():
    now = timezone.now()
    miner_cap = Object.objects.create(
        aodp_id="TEST_T4_HEAD_GATHERER_ORE_VIEW",
        name="Adept's Miner Cap",
        type_id=ObjectType.HEAD,
        tier=4,
        enchantment=2,
        crafting_tree="gatherer_ore_head",
    )
    miner_garb = Object.objects.create(
        aodp_id="TEST_T4_ARMOR_GATHERER_ORE_VIEW",
        name="Adept's Miner Garb",
        type_id=ObjectType.ARMOR,
        tier=4,
        enchantment=2,
        equipment_category="CHEST",
        crafting_tree="gatherer_ore_chest",
    )
    miner_workboot = Object.objects.create(
        aodp_id="TEST_T4_SHOES_GATHERER_ORE_VIEW",
        name="Adept's Miner Workboot",
        type_id=ObjectType.SHOES,
        tier=4,
        enchantment=2,
        equipment_category="SHOE",
        crafting_tree="gatherer_ore_shoe",
    )
    miner_backpack = Object.objects.create(
        aodp_id="TEST_T4_BACKPACK_GATHERER_ORE_VIEW",
        name="Adept's Miner Backpack",
        type_id=ObjectType.BACKPACK,
        tier=4,
        enchantment=2,
    )
    metal_bar = Object.objects.create(
        aodp_id="TEST_T4_METALBAR_VIEW@2",
        name="Adept's Metal Bar",
        type_id=ObjectType.METALBAR,
        tier=4,
        enchantment=2,
    )
    cloth = Object.objects.create(
        aodp_id="TEST_T4_CLOTH_VIEW@2",
        name="Adept's Cloth",
        type_id=ObjectType.CLOTH,
        tier=4,
        enchantment=2,
    )
    leather = Object.objects.create(
        aodp_id="TEST_T4_LEATHER_VIEW@2",
        name="Adept's Leather",
        type_id=ObjectType.LEATHER,
        tier=4,
        enchantment=2,
    )

    for gear_object in [miner_cap, miner_garb, miner_workboot, miner_backpack]:
        for city, timestamp, quality_payloads in [
            (
                City.BRIDGEWATCH,
                now - timedelta(minutes=30),
                [(0, 100, 400), (1, 200, 500), (2, 300, 600)],
            ),
            (
                City.FORT_STERLING,
                now - timedelta(minutes=30),
                [(0, 120, 420), (1, 220, 520), (2, 320, 620)],
            ),
        ]:
            for quality, sell_price_min, buy_price_max in quality_payloads:
                Price.objects.create(
                    object=gear_object,
                    city=city,
                    quality=quality,
                    sell_price_min=sell_price_min,
                    sell_price_min_date=timestamp,
                    buy_price_max=buy_price_max,
                    buy_price_max_date=timestamp,
                )

    for input_object in [metal_bar, cloth, leather]:
        for city, timestamp, quality_payloads in [
            (
                City.BRIDGEWATCH,
                now - timedelta(minutes=30),
                [(0, 4, 8), (1, 5, 9), (2, 6, 10)],
            ),
            (
                City.FORT_STERLING,
                now - timedelta(minutes=30),
                [(0, 6, 10), (1, 7, 11), (2, 8, 12)],
            ),
        ]:
            for quality, sell_price_min, buy_price_max in quality_payloads:
                Price.objects.create(
                    object=input_object,
                    city=city,
                    quality=quality,
                    sell_price_min=sell_price_min,
                    sell_price_min_date=timestamp,
                    buy_price_max=buy_price_max,
                    buy_price_max_date=timestamp,
                )

    miner_cap_recipe = Recipe.objects.create(output=miner_cap, output_quantity=1)
    RecipeInput.objects.create(recipe=miner_cap_recipe, object=metal_bar, quantity=8)
    miner_garb_recipe = Recipe.objects.create(output=miner_garb, output_quantity=1)
    RecipeInput.objects.create(recipe=miner_garb_recipe, object=metal_bar, quantity=8)
    miner_workboot_recipe = Recipe.objects.create(output=miner_workboot, output_quantity=1)
    RecipeInput.objects.create(recipe=miner_workboot_recipe, object=metal_bar, quantity=8)
    miner_backpack_recipe = Recipe.objects.create(output=miner_backpack, output_quantity=1)
    RecipeInput.objects.create(recipe=miner_backpack_recipe, object=cloth, quantity=4)
    RecipeInput.objects.create(recipe=miner_backpack_recipe, object=leather, quantity=4)

    return {
        "miner_cap": miner_cap,
        "miner_garb": miner_garb,
        "miner_workboot": miner_workboot,
        "miner_backpack": miner_backpack,
    }


def _create_fish_gathering_gear_sample():
    now = timezone.now()
    fisherman_cap = Object.objects.create(
        aodp_id="TEST_T4_HEAD_GATHERER_FISH_VIEW",
        name="Adept's Fisherman Cap",
        type_id=ObjectType.HEAD,
        tier=4,
        enchantment=2,
        crafting_tree="gatherer_fish_head",
    )
    fisherman_garb = Object.objects.create(
        aodp_id="TEST_T4_ARMOR_GATHERER_FISH_VIEW",
        name="Adept's Fisherman Garb",
        type_id=ObjectType.ARMOR,
        tier=4,
        enchantment=2,
        equipment_category="CHEST",
        crafting_tree="gatherer_fish_chest",
    )
    fisherman_workboot = Object.objects.create(
        aodp_id="TEST_T4_SHOES_GATHERER_FISH_VIEW",
        name="Adept's Fisherman Workboots",
        type_id=ObjectType.SHOES,
        tier=4,
        enchantment=2,
        equipment_category="SHOE",
        crafting_tree="gatherer_fish_shoe",
    )
    fisherman_backpack = Object.objects.create(
        aodp_id="TEST_T4_BACKPACK_GATHERER_FISH_VIEW",
        name="Adept's Fisherman Backpack",
        type_id=ObjectType.BACKPACK,
        tier=4,
        enchantment=2,
    )
    cloth = Object.objects.create(
        aodp_id="TEST_T4_CLOTH_FISH_VIEW@2",
        name="Adept's Cloth",
        type_id=ObjectType.CLOTH,
        tier=4,
        enchantment=2,
    )
    leather = Object.objects.create(
        aodp_id="TEST_T4_LEATHER_FISH_VIEW@2",
        name="Adept's Leather",
        type_id=ObjectType.LEATHER,
        tier=4,
        enchantment=2,
    )

    for gear_object in [fisherman_cap, fisherman_garb, fisherman_workboot, fisherman_backpack]:
        for city, timestamp, quality_payloads in [
            (
                City.BRIDGEWATCH,
                now - timedelta(minutes=30),
                [(0, 100, 400), (1, 200, 500), (2, 300, 600)],
            ),
            (
                City.FORT_STERLING,
                now - timedelta(minutes=30),
                [(0, 120, 420), (1, 220, 520), (2, 320, 620)],
            ),
        ]:
            for quality, sell_price_min, buy_price_max in quality_payloads:
                Price.objects.create(
                    object=gear_object,
                    city=city,
                    quality=quality,
                    sell_price_min=sell_price_min,
                    sell_price_min_date=timestamp,
                    buy_price_max=buy_price_max,
                    buy_price_max_date=timestamp,
                )

    for input_object in [cloth, leather]:
        for city, timestamp, quality_payloads in [
            (
                City.BRIDGEWATCH,
                now - timedelta(minutes=30),
                [(0, 4, 8), (1, 5, 9), (2, 6, 10)],
            ),
            (
                City.FORT_STERLING,
                now - timedelta(minutes=30),
                [(0, 6, 10), (1, 7, 11), (2, 8, 12)],
            ),
        ]:
            for quality, sell_price_min, buy_price_max in quality_payloads:
                Price.objects.create(
                    object=input_object,
                    city=city,
                    quality=quality,
                    sell_price_min=sell_price_min,
                    sell_price_min_date=timestamp,
                    buy_price_max=buy_price_max,
                    buy_price_max_date=timestamp,
                )

    fisherman_cap_recipe = Recipe.objects.create(output=fisherman_cap, output_quantity=1)
    RecipeInput.objects.create(recipe=fisherman_cap_recipe, object=leather, quantity=8)
    fisherman_garb_recipe = Recipe.objects.create(output=fisherman_garb, output_quantity=1)
    RecipeInput.objects.create(recipe=fisherman_garb_recipe, object=leather, quantity=8)
    fisherman_workboot_recipe = Recipe.objects.create(output=fisherman_workboot, output_quantity=1)
    RecipeInput.objects.create(recipe=fisherman_workboot_recipe, object=leather, quantity=8)
    fisherman_backpack_recipe = Recipe.objects.create(output=fisherman_backpack, output_quantity=1)
    RecipeInput.objects.create(recipe=fisherman_backpack_recipe, object=cloth, quantity=4)
    RecipeInput.objects.create(recipe=fisherman_backpack_recipe, object=leather, quantity=4)

    return {
        "fisherman_cap": fisherman_cap,
        "fisherman_garb": fisherman_garb,
        "fisherman_workboot": fisherman_workboot,
        "fisherman_backpack": fisherman_backpack,
    }


@pytest.mark.django_db
class TestGatheringGearView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="albion-online-gathering-gear-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_get_returns_page(self, authenticated_client):
        sample_objects = _create_ore_gathering_gear_sample()

        response = authenticated_client.get(f"{reverse('albion_online:gathering_gear')}?city=all&resource=all")
        response_content = response.content.decode()
        resource_filter_match = re.search(
            r'<select id="resourceFilter"[^>]*>(.*?)</select>',
            response_content,
            flags=re.S,
        )

        assert response.status_code == 200
        assert b'name="city"' in response.content
        assert b'name="resource"' in response.content
        assert b'value="ore" selected' in response.content
        assert b"Ore market tracker" in response.content
        assert resource_filter_match is not None
        assert 'value="all"' not in resource_filter_match.group(1)
        assert b"marketDetailPanel" in response.content
        assert b"marketDetailPanelBody" in response.content
        assert b"market-tier-cell" in response.content
        assert b"data-detail-target=\"BRIDGEWATCH\"" in response.content
        assert b"data-detail-panel-url" in response.content
        assert b"Refresh Price" in response.content
        assert b"Gathering Gear" in response.content
        assert b"Cap" in response.content
        assert b"Garb" in response.content
        assert b"Workboot" in response.content
        assert b"Backpack" in response.content
        assert b"TEST_T4_HEAD_GATHERER_ORE_VIEW" not in response.content
        assert b"T4.2" in response.content
        assert b"Select a row to load details." in response.content

    def test_get_lists_fish_resource_filter_option(self, authenticated_client):
        _create_fish_gathering_gear_sample()

        response = authenticated_client.get(f"{reverse('albion_online:gathering_gear')}?resource=fish")

        assert response.status_code == 200
        assert b'value="fish" selected' in response.content
        assert b"Fish market tracker" in response.content
        assert b'data-detail-key="fish:HEAD:4.2"' in response.content

    def test_get_falls_back_to_ore_when_resource_is_invalid(self, authenticated_client):
        _create_ore_gathering_gear_sample()

        response = authenticated_client.get(f"{reverse('albion_online:gathering_gear')}?resource=all")

        assert response.status_code == 200
        assert b'value="ore" selected' in response.content
        assert b"Ore market tracker" in response.content

    def test_get_maps_stone_resource_filter_to_rock(self, authenticated_client):
        _create_ore_gathering_gear_sample()

        response = authenticated_client.get(f"{reverse('albion_online:gathering_gear')}?resource=stone")

        assert response.status_code == 200
        assert b'value="rock" selected' in response.content
        assert b"Rock market tracker" in response.content

    def test_get_filters_to_fort_sterling_by_default(self, authenticated_client):
        _create_ore_gathering_gear_sample()

        response = authenticated_client.get(reverse("albion_online:gathering_gear"))

        assert response.status_code == 200
        assert b'value="FORT_STERLING" selected' in response.content
        assert b"<h2 class=\"h5 mb-0\">Fort Sterling</h2>" in response.content
        assert b"<h2 class=\"h5 mb-0\">Bridgewatch</h2>" not in response.content

    def test_get_can_filter_to_all_cities(self, authenticated_client):
        _create_ore_gathering_gear_sample()

        response = authenticated_client.get(f"{reverse('albion_online:gathering_gear')}?city=all&resource=ore")

        assert response.status_code == 200
        assert b'value="all" selected' in response.content
        assert b"<h2 class=\"h5 mb-0\">Fort Sterling</h2>" in response.content
        assert b"<h2 class=\"h5 mb-0\">Bridgewatch</h2>" in response.content

    def test_detail_panel_endpoint_returns_fragment(self, authenticated_client):
        _create_ore_gathering_gear_sample()

        response = authenticated_client.get(
            f"{reverse('albion_online:gathering_gear_detail_panel')}?detail_key=ore:HEAD:4.2"
        )

        assert response.status_code == 200
        assert b'data-detail-key="ore:HEAD:4.2"' in response.content
        assert b"Bridgewatch" in response.content
        assert b"Craft cost:" in response.content

    def test_post_refreshes_prices(self, authenticated_client, monkeypatch):
        gathering_gear_view = import_module("albion_online.views.gathering_gear")

        called = {"delay": None}

        class FakeDelay:
            def delay(self, **kwargs):
                called["delay"] = kwargs

        monkeypatch.setattr(gathering_gear_view, "refresh_price_job", FakeDelay())

        response = authenticated_client.post(
            f"{reverse('albion_online:gathering_gear')}?city=all&resource=ore"
        )

        assert response.status_code == 302
        assert "refresh_job_id=" in response.url
        assert response.url.startswith(f"{reverse('albion_online:gathering_gear')}?city=all&resource=ore")
        assert called["delay"] is not None
        job = PriceRefreshJob.objects.get()
        assert job.kind == PriceRefreshJob.Kind.GATHERING_GEAR
        assert job.status == PriceRefreshJob.Status.QUEUED

    def test_price_refresh_job_status_returns_json(self, authenticated_client):
        job = PriceRefreshJob.objects.create(
            kind=PriceRefreshJob.Kind.GATHERING_GEAR,
            status=PriceRefreshJob.Status.SUCCESS,
            refreshed_count=34,
        )

        response = authenticated_client.get(
            reverse("albion_online:price_refresh_job_status", kwargs={"job_id": job.id})
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["refreshed_count"] == 34

    def test_profitability_page_omits_resource_filter(self, authenticated_client):
        _create_ore_gathering_gear_sample()

        response = authenticated_client.get(f"{reverse('albion_online:gathering_gear_profitability')}?city=all")

        assert response.status_code == 200
        assert b"Profitable crafts" in response.content
        assert b'name="resource"' not in response.content

    def test_marking_a_profitability_row_done_hides_it_for_twelve_hours(self, authenticated_client):
        sample_objects = _create_ore_gathering_gear_sample()

        post_response = authenticated_client.post(
            f"{reverse('albion_online:craft_profitability_mark_done')}?city=BRIDGEWATCH&resource=ore",
            data={
                "object_aodp_id": sample_objects["miner_cap"].aodp_id,
                "row_city": City.BRIDGEWATCH,
                "return_url": f"{reverse('albion_online:gathering_gear_profitability')}?city=BRIDGEWATCH&resource=ore",
            },
        )

        assert post_response.status_code == 302
        assert post_response.url == f"{reverse('albion_online:gathering_gear_profitability')}?city=BRIDGEWATCH&resource=ore"
        assert CraftProfitabilityDone.objects.filter(
            object=sample_objects["miner_cap"],
            city=City.BRIDGEWATCH,
        ).exists()

        response = authenticated_client.get(f"{reverse('albion_online:gathering_gear_profitability')}?city=BRIDGEWATCH")

        assert response.status_code == 200
        assert b"Miner Cap" not in response.content

    def test_done_profitability_row_reappears_after_twelve_hours(self, authenticated_client):
        sample_objects = _create_ore_gathering_gear_sample()
        CraftProfitabilityDone.objects.create(
            object=sample_objects["miner_cap"],
            city=City.BRIDGEWATCH,
            completed_at=timezone.now() - timedelta(hours=13),
        )

        response = authenticated_client.get(f"{reverse('albion_online:gathering_gear_profitability')}?city=BRIDGEWATCH")

        assert response.status_code == 200
        assert b"Miner Cap" in response.content
