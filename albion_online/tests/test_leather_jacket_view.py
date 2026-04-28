from importlib import import_module
from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from albion_online.constants.city import City
from albion_online.constants.object_type import ObjectType
from albion_online.models import Object, Price, Recipe, RecipeInput


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

        response = authenticated_client.get(reverse("albion_online:leather_jacket"))

        assert response.status_code == 200
        assert b"marketDetailPanel" in response.content
        assert b"data-detail-target=\"all\"" in response.content
        assert b"data-detail-target=\"BRIDGEWATCH\"" in response.content
        assert b"data-market-city=\"BRIDGEWATCH\"" in response.content
        assert b"Normal" in response.content
        assert b"Good" in response.content
        assert b"Outstanding" in response.content
        assert b"Excellent" in response.content
        assert b"Masterpiece" in response.content
        assert b"Refresh Price" in response.content
        assert b"Mercenary Jacket variants" in response.content
        assert b"Mercenary Jacket 4.2" in response.content
        assert b"TEST_T4_ARMOR_LEATHER_SET1_MARKET" not in response.content
        assert b"T4.2" not in response.content
        assert b"Bridgewatch" in response.content
        assert b"Caerleon" in response.content
        assert b"Martlock" in response.content
        assert b"+127 (+184.1%)" in response.content
        assert "✕" in response.content.decode()
        assert "🕒" in response.content.decode()
        assert b"Craft cost:" in response.content
        assert b"68" in response.content
        assert b"69" in response.content
        assert b"bg-warning" in response.content
        assert b"Buy" not in response.content
        assert b"Sell price min date" not in response.content
        assert b"Buy price max date" not in response.content
        assert b"678" in response.content
        assert "Infos masquées car un des prix a plus d'un jour." not in response.content.decode()

    def test_post_refreshes_prices(self, authenticated_client, monkeypatch):
        called = {"refresh": False}
        leather_jacket_view = import_module("albion_online.views.leather_jacket")

        class FakeService:
            def refresh_prices(self):
                called["refresh"] = True
                return [object()]

        monkeypatch.setattr(leather_jacket_view, "MercenaryJacketPriceRefreshService", lambda: FakeService())

        response = authenticated_client.post(reverse("albion_online:leather_jacket"))

        assert response.status_code == 302
        assert called["refresh"] is True
