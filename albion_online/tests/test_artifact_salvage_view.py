from importlib import import_module
from datetime import timedelta
import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from albion_online.constants.city import City
from albion_online.constants.object_type import ObjectType
from albion_online.models import Object, Price, PriceRefreshJob


def _create_object(aodp_id, type_id, tier):
    return Object.objects.create(
        aodp_id=aodp_id,
        name=aodp_id,
        type_id=type_id,
        tier=tier,
        enchantment=0,
    )


@pytest.mark.django_db
class TestArtifactSalvageView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="albion-online-artifact-salvage-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_get_returns_page(self, authenticated_client):
        now = timezone.now()
        shard_t6 = _create_object("TEST_RUNE_SHARD_T6_VIEW", ObjectType.RUNE, 6)
        artifact_t6 = _create_object(
            "TEST_RUNE_ARTIFACT_T6_ARTEFACT_MAIN_SCIMITAR_MORGANA_VIEW",
            ObjectType.ARTEFACT,
            6,
        )
        shard_t7 = _create_object("TEST_RUNE_SHARD_T7_VIEW", ObjectType.RUNE, 7)
        artifact_t7 = _create_object(
            "TEST_RUNE_ARTIFACT_T7_ARTEFACT_MAIN_SCIMITAR_MORGANA_VIEW",
            ObjectType.ARTEFACT,
            7,
        )
        shard_t8 = _create_object("TEST_RUNE_SHARD_T8_VIEW", ObjectType.RUNE, 8)
        artifact_t8 = _create_object(
            "TEST_RUNE_ARTIFACT_T8_ARTEFACT_MAIN_SCIMITAR_MORGANA_VIEW",
            ObjectType.ARTEFACT,
            8,
        )

        for albion_object, prices in [
            (shard_t6, [100, 110, 120]),
            (artifact_t6, [800, 820, 840]),
            (shard_t7, [200, 210, 220]),
            (artifact_t7, [1600, 1620, 1640]),
            (shard_t8, [300, 310, 320]),
            (artifact_t8, [2400, 2420, 2440]),
        ]:
            for quality, sell_price_min in enumerate(prices):
                Price.objects.create(
                    object=albion_object,
                    city=City.FORT_STERLING,
                    quality=quality,
                    sell_price_min=sell_price_min,
                    sell_price_min_date=now - timedelta(minutes=quality),
                    buy_price_max=sell_price_min + 25,
                    buy_price_max_date=now - timedelta(minutes=quality),
                )

        response = authenticated_client.get(reverse("albion_online:artifact_salvage"))

        assert response.status_code == 200
        assert b"Artifact salvage market tracker" in response.content
        assert b"value=\"FORT_STERLING\" selected" in response.content
        assert b"Refresh Price" in response.content
        assert b"Rune" in response.content
        assert b"Soul" in response.content
        assert b"Relic" in response.content
        assert b"Avalonian" in response.content
        assert b"Rune x10" in response.content
        assert b"Buy order" in response.content
        assert b"Bloodforged Blade" in response.content
        assert b"artifact-salvage-price-green-pale" in response.content
        assert b"artifact-salvage-price-green-strong" in response.content
        assert b'title="Dernier prix: il y a 0 heures"' in response.content

    def test_get_rejects_invalid_city_and_uses_default(self, authenticated_client):
        response = authenticated_client.get(f"{reverse('albion_online:artifact_salvage')}?city=all")

        assert response.status_code == 200
        assert b"value=\"FORT_STERLING\" selected" in response.content
        assert b"value=\"all\" selected" not in response.content

    def test_post_refreshes_prices(self, authenticated_client, monkeypatch):
        artifact_salvage_view = import_module("albion_online.views.artifact_salvage")

        called = {"delay": None}

        class FakeDelay:
            def delay(self, **kwargs):
                called["delay"] = kwargs

        monkeypatch.setattr(artifact_salvage_view, "refresh_price_job", FakeDelay())

        response = authenticated_client.post(reverse("albion_online:artifact_salvage"))

        assert response.status_code == 302
        assert "refresh_job_id=" in response.url
        assert response.url.startswith(f"{reverse('albion_online:artifact_salvage')}?city=FORT_STERLING")
        assert called["delay"] is not None
        job = PriceRefreshJob.objects.get()
        assert job.kind == PriceRefreshJob.Kind.ARTIFACT_SALVAGE
        assert job.status == PriceRefreshJob.Status.QUEUED

    def test_debug_refresh_targets_returns_aodp_item_ids(self, authenticated_client):
        _create_object("TEST_RUNE_SHARD_T6_VIEW", ObjectType.RUNE, 6)
        _create_object(
            "TEST_RUNE_ARTIFACT_T6_ARTEFACT_MAIN_SCIMITAR_MORGANA_VIEW",
            ObjectType.ARTEFACT,
            6,
        )

        response = authenticated_client.get(
            reverse("albion_online:artifact_salvage_refresh_targets")
        )

        payload = json.loads(response.content)

        assert response.status_code == 200
        assert payload["batch_count"] >= 1
        assert "TEST_RUNE_ARTIFACT_T6_ARTEFACT_MAIN_SCIMITAR_MORGANA_VIEW" in payload["item_ids"]
        assert "TEST_RUNE_SHARD_T6_VIEW" in payload["item_ids"]
        assert payload["families"][0]["key"] == "rune"
        assert "TEST_RUNE_ARTIFACT_T6_ARTEFACT_MAIN_SCIMITAR_MORGANA_VIEW" in payload["families"][0]["item_ids"]
        assert "TEST_RUNE_SHARD_T6_VIEW" in payload["families"][0]["item_ids"]
