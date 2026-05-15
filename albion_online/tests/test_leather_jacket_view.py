from importlib import import_module
from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from albion_online.constants.city import City
from albion_online.constants.object_type import ObjectType
from albion_online.models import Object, Price, PriceRefreshJob, Recipe, RecipeInput


@pytest.mark.django_db
class TestLeatherJacketView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="albion-online-leather-jacket-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_get_returns_page(self, authenticated_client):
        now = timezone.now()
        object_instance = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_LEATHER_SET1_MARKET",
            name="Adept's Mercenary Jacket",
            type_id=ObjectType.ARMOR,
            tier=4,
            enchantment=2,
            equipment_category="CHEST",
            crafting_tree="leather_chest",
        )
        leather = Object.objects.create(
            aodp_id="TEST_T4_LEATHER_LEVEL1_MARKET@2",
            name="Adept's Leather",
            type_id=ObjectType.LEATHER,
            tier=4,
            enchantment=2,
            crafting_tree="leather_chest",
        )
        recipe = Recipe.objects.create(output=object_instance, output_quantity=1)
        RecipeInput.objects.create(recipe=recipe, object=leather, quantity=16)

        city_payloads = [
            (
                City.BRIDGEWATCH,
                now - timedelta(minutes=30),
                [(0, 100, 400), (1, 200, 500), (2, 300, 600)],
            ),
            (
                City.CAERLEON,
                now - timedelta(hours=2),
                [(0, 1000, 1300), (1, 1100, 1400), (2, 1200, 1500)],
            ),
            (
                City.MARTLOCK,
                now - timedelta(days=2),
                [(0, 2000, 2300), (1, 2100, 2400), (2, 2200, 2500)],
            ),
        ]

        for city, timestamp, quality_payloads in city_payloads:
            for quality, sell_price_min, buy_price_max in quality_payloads:
                Price.objects.create(
                    object=object_instance,
                    city=city,
                    quality=quality,
                    sell_price_min=sell_price_min,
                    sell_price_min_date=timestamp,
                    buy_price_max=buy_price_max,
                    buy_price_max_date=timestamp,
                )

        leather_city_payloads = [
            (
                City.BRIDGEWATCH,
                now - timedelta(minutes=30),
                [(0, 4, 8), (1, 5, 9), (2, 6, 10)],
            ),
            (
                City.CAERLEON,
                now - timedelta(hours=2),
                [(0, 100, 130), (1, 100, 140), (2, 100, 150)],
            ),
            (
                City.MARTLOCK,
                now - timedelta(days=2),
                [(0, 50, 80), (1, 50, 90), (2, 50, 100)],
            ),
        ]

        for city, timestamp, quality_payloads in leather_city_payloads:
            for quality, sell_price_min, buy_price_max in quality_payloads:
                Price.objects.create(
                    object=leather,
                    city=city,
                    quality=quality,
                    sell_price_min=sell_price_min,
                    sell_price_min_date=timestamp,
                    buy_price_max=buy_price_max,
                    buy_price_max_date=timestamp,
                )

        response = authenticated_client.get(f"{reverse('albion_online:leather_jacket')}?city=all")

        assert response.status_code == 200
        assert b'name="city"' in response.content
        assert b'value="all" selected' in response.content
        assert b"marketDetailPanel" in response.content
        assert b"marketDetailPanelBody" in response.content
        assert b"market-tier-cell" in response.content
        assert b"data-detail-target=\"BRIDGEWATCH\"" in response.content
        assert b"data-detail-panel-url" in response.content
        assert b"Refresh Price" in response.content
        assert b"Leather Jacket market tracker" in response.content
        assert b"Mercenary" in response.content
        assert b"Hunter" in response.content
        assert b"Assassin" in response.content
        assert b"Stalker" in response.content
        assert b"Hellion" in response.content
        assert b"Specter" in response.content
        assert b"Tenacity" in response.content
        assert b"Mistwalker" in response.content
        assert b"Mercenary Jacket 4.2" in response.content
        assert b"TEST_T4_ARMOR_LEATHER_SET1_MARKET" not in response.content
        assert b"T4.2" in response.content
        assert b"Select a row to load details." in response.content

    def test_get_filters_to_fort_sterling_by_default(self, authenticated_client):
        response = authenticated_client.get(reverse("albion_online:leather_jacket"))

        assert response.status_code == 200
        assert b'value="FORT_STERLING" selected' in response.content
        assert b"<h2 class=\"h5 mb-0\">Fort Sterling</h2>" in response.content
        assert b"<h2 class=\"h5 mb-0\">Bridgewatch</h2>" not in response.content

    def test_get_can_filter_to_all_cities(self, authenticated_client):
        response = authenticated_client.get(f"{reverse('albion_online:leather_jacket')}?city=all")

        assert response.status_code == 200
        assert b'value="all" selected' in response.content
        assert b"<h2 class=\"h5 mb-0\">Fort Sterling</h2>" in response.content
        assert b"<h2 class=\"h5 mb-0\">Bridgewatch</h2>" in response.content

    def test_detail_panel_endpoint_returns_fragment(self, authenticated_client):
        now = timezone.now()
        object_instance = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_LEATHER_SET1_DETAIL",
            name="Adept's Mercenary Jacket",
            type_id=ObjectType.ARMOR,
            tier=4,
            enchantment=2,
            equipment_category="CHEST",
            crafting_tree="leather_chest",
        )
        leather = Object.objects.create(
            aodp_id="TEST_T4_LEATHER_LEVEL1_DETAIL@2",
            name="Adept's Leather",
            type_id=ObjectType.LEATHER,
            tier=4,
            enchantment=2,
            crafting_tree="leather_chest",
        )
        recipe = Recipe.objects.create(output=object_instance, output_quantity=1)
        RecipeInput.objects.create(recipe=recipe, object=leather, quantity=16)

        for city, sell_price_min, buy_price_max in [
            (City.BRIDGEWATCH, 100, 400),
            (City.CAERLEON, 1000, 1300),
        ]:
            for quality in range(3):
                Price.objects.create(
                    object=object_instance,
                    city=city,
                    quality=quality,
                    sell_price_min=sell_price_min,
                    sell_price_min_date=now,
                    buy_price_max=buy_price_max,
                    buy_price_max_date=now,
                )
                Price.objects.create(
                    object=leather,
                    city=city,
                    quality=quality,
                    sell_price_min=5,
                    sell_price_min_date=now,
                    buy_price_max=9,
                    buy_price_max_date=now,
                )

        response = authenticated_client.get(
            f"{reverse('albion_online:leather_jacket_detail_panel')}?detail_key=mercenary:4.2"
        )

        assert response.status_code == 200
        assert b'data-detail-key="mercenary:4.2"' in response.content
        assert b"Bridgewatch" in response.content
        assert b"Craft cost:" in response.content

    def test_post_refreshes_prices(self, authenticated_client, monkeypatch):
        leather_jacket_view = import_module("albion_online.views.leather_jacket")

        called = {"delay": None}

        class FakeDelay:
            def delay(self, **kwargs):
                called["delay"] = kwargs

        monkeypatch.setattr(leather_jacket_view, "refresh_price_job", FakeDelay())

        response = authenticated_client.post(f"{reverse('albion_online:leather_jacket')}?city=all")

        assert response.status_code == 302
        assert "refresh_job_id=" in response.url
        assert response.url.startswith(f"{reverse('albion_online:leather_jacket')}?city=all")
        assert called["delay"] is not None
        job = PriceRefreshJob.objects.get()
        assert job.kind == PriceRefreshJob.Kind.LEATHER_JACKET
        assert job.status == PriceRefreshJob.Status.QUEUED

    def test_price_refresh_job_status_returns_json(self, authenticated_client):
        job = PriceRefreshJob.objects.create(
            kind=PriceRefreshJob.Kind.LEATHER_JACKET,
            status=PriceRefreshJob.Status.SUCCESS,
            refreshed_count=12,
        )

        response = authenticated_client.get(
            reverse("albion_online:price_refresh_job_status", kwargs={"job_id": job.id})
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["refreshed_count"] == 12
