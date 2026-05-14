from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from albion_online.constants.city import City
from albion_online.constants.object_type import ObjectType
from albion_online.models import CraftProfitabilityDone, Object, Price, Recipe, RecipeInput


def _add_price_series(albion_object, city, sell_price_min, buy_price_max, timestamp):
    for quality in range(3):
        Price.objects.create(
            object=albion_object,
            city=city,
            quality=quality,
            sell_price_min=sell_price_min,
            sell_price_min_date=timestamp,
            buy_price_max=buy_price_max,
            buy_price_max_date=timestamp,
        )


def _seed_profitability_data():
    now = timezone.now()
    leather = Object.objects.create(
        aodp_id="TEST_T4_LEATHER_LEVEL1_PROFITABILITY@2",
        name="Adept's Leather",
        type_id=ObjectType.LEATHER,
        tier=4,
        enchantment=2,
        crafting_tree="leather_chest",
    )
    _add_price_series(leather, City.BRIDGEWATCH, 5, 9, now - timedelta(minutes=30))

    mercenary_jacket = Object.objects.create(
        aodp_id="TEST_T4_ARMOR_LEATHER_SET1_PROFITABILITY",
        name="Adept's Mercenary Jacket",
        type_id=ObjectType.ARMOR,
        tier=4,
        enchantment=2,
        equipment_category="CHEST",
        crafting_tree="leather_chest",
    )
    mercenary_recipe = Recipe.objects.create(output=mercenary_jacket, output_quantity=1)
    RecipeInput.objects.create(recipe=mercenary_recipe, object=leather, quantity=16)
    _add_price_series(mercenary_jacket, City.BRIDGEWATCH, 200, 240, now - timedelta(minutes=30))

    hunter_jacket = Object.objects.create(
        aodp_id="TEST_T4_ARMOR_LEATHER_SET2_PROFITABILITY",
        name="Adept's Hunter Jacket",
        type_id=ObjectType.ARMOR,
        tier=4,
        enchantment=2,
        equipment_category="CHEST",
        crafting_tree="leather_chest",
    )
    hunter_recipe = Recipe.objects.create(output=hunter_jacket, output_quantity=1)
    RecipeInput.objects.create(recipe=hunter_recipe, object=leather, quantity=64)
    _add_price_series(hunter_jacket, City.BRIDGEWATCH, 500, 580, now - timedelta(minutes=30))

    assassin_jacket = Object.objects.create(
        aodp_id="TEST_T4_ARMOR_LEATHER_SET3_PROFITABILITY",
        name="Adept's Assassin Jacket",
        type_id=ObjectType.ARMOR,
        tier=4,
        enchantment=2,
        equipment_category="CHEST",
        crafting_tree="leather_chest",
    )
    assassin_recipe = Recipe.objects.create(output=assassin_jacket, output_quantity=1)
    RecipeInput.objects.create(recipe=assassin_recipe, object=leather, quantity=16)
    _add_price_series(assassin_jacket, City.BRIDGEWATCH, 25, 30, now - timedelta(minutes=30))


@pytest.mark.django_db
class TestLeatherJacketProfitabilityView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="albion-online-leather-jacket-profitability-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_get_returns_profitable_rows_and_default_sort_is_percentage(self, authenticated_client):
        _seed_profitability_data()

        response = authenticated_client.get(f"{reverse('albion_online:leather_jacket_profitability')}?city=all")

        assert response.status_code == 200
        assert b"Profitable crafts" in response.content
        assert b"Only rows with a positive margin" in response.content
        assert b'name="city"' in response.content
        assert b'name="jacket_type"' in response.content
        assert b'name="min_percentage"' in response.content
        assert b'value="20.0"' in response.content
        assert b'name="min_flat"' in response.content
        assert b'name="sort"' in response.content
        assert b'value="percentage" selected' in response.content
        assert b"Mercenary Jacket" in response.content
        assert b"Hunter Jacket" in response.content
        assert b"Assassin Jacket" not in response.content
        assert b"marketDetailPanel" in response.content
        assert b"market-profitability-row" in response.content
        assert b"data-detail-key=" in response.content
        assert response.content.index(b"Mercenary Jacket") < response.content.index(b"Hunter Jacket")
        assert b"Bridgewatch" in response.content
        assert b"+127" in response.content
        assert b"+214" in response.content

    def test_get_can_sort_by_flat_amount(self, authenticated_client):
        _seed_profitability_data()

        response = authenticated_client.get(
            f"{reverse('albion_online:leather_jacket_profitability')}?city=all&sort=flat"
        )

        assert response.status_code == 200
        assert b'value="flat" selected' in response.content
        assert response.content.index(b"Hunter Jacket") < response.content.index(b"Mercenary Jacket")
        assert b"+214" in response.content

    def test_marking_a_profitability_row_done_hides_it_for_twelve_hours(self, authenticated_client):
        _seed_profitability_data()

        post_response = authenticated_client.post(
            f"{reverse('albion_online:craft_profitability_mark_done')}?city=BRIDGEWATCH&jacket_type=all",
            data={
                "object_aodp_id": "TEST_T4_ARMOR_LEATHER_SET1_PROFITABILITY",
                "row_city": City.BRIDGEWATCH,
                "return_url": f"{reverse('albion_online:leather_jacket_profitability')}?city=BRIDGEWATCH&jacket_type=all",
            },
        )

        assert post_response.status_code == 302
        assert post_response.url == f"{reverse('albion_online:leather_jacket_profitability')}?city=BRIDGEWATCH&jacket_type=all"
        assert CraftProfitabilityDone.objects.filter(
            object__aodp_id="TEST_T4_ARMOR_LEATHER_SET1_PROFITABILITY",
            city=City.BRIDGEWATCH,
        ).exists()

        response = authenticated_client.get(f"{reverse('albion_online:leather_jacket_profitability')}?city=BRIDGEWATCH")

        assert response.status_code == 200
        assert b"Mercenary Jacket" not in response.content

    def test_done_profitability_row_reappears_after_twelve_hours(self, authenticated_client):
        _seed_profitability_data()
        mercenary_jacket = Object.objects.get(aodp_id="TEST_T4_ARMOR_LEATHER_SET1_PROFITABILITY")
        CraftProfitabilityDone.objects.create(
            object=mercenary_jacket,
            city=City.BRIDGEWATCH,
            completed_at=timezone.now() - timedelta(hours=13),
        )

        response = authenticated_client.get(f"{reverse('albion_online:leather_jacket_profitability')}?city=BRIDGEWATCH")

        assert response.status_code == 200
        assert b"Mercenary Jacket" in response.content
