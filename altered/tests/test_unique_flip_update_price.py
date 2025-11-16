from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from altered.models import UniqueFlip, UniquePrice


@pytest.mark.django_db
def test_update_price_button_sets_current_price_to_advised_price(client):
    now = timezone.now()

    with patch('altered.signals.AlteredFetchUniqueDataService') as mocked_service:
        mocked_service.return_value.handle.return_value = None

        flip = UniqueFlip.objects.create(
            unique_id='UF999',
            name='Test Flip',
            bought_at=now - timedelta(days=10),
            bought_price=Decimal('50.00'),
            advised_price=Decimal('40.00'),
        )
        UniquePrice.objects.create(
            date=now - timedelta(days=5),
            price=Decimal('60.00'),
            unique_flip=flip,
        )

    url = reverse('altered:unique_flip_list') + '?status=current'
    user = get_user_model().objects.create_user('tester', password='pass1234')
    user.is_staff = True
    user.save(update_fields=['is_staff'])
    client.force_login(user)
    response = client.post(url, {
        'update_price': '1',
        'flip_id': flip.id,
    })

    assert response.status_code == 302

    flip.refresh_from_db()
    assert flip.advised_price is None
    assert flip.current_price == Decimal('40.00')
    assert flip.prices.first().price == Decimal('40.00')


@pytest.mark.django_db
def test_update_all_prices_updates_only_expected_flips(client):
    now = timezone.now()

    with patch('altered.signals.AlteredFetchUniqueDataService') as mocked_service:
        mocked_service.return_value.handle.return_value = None

        flip_should_update = UniqueFlip.objects.create(
            unique_id='UF100',
            name='Needs Bulk Update',
            bought_at=now - timedelta(days=8),
            bought_price=Decimal('30.00'),
            advised_price=Decimal('35.00'),
            in_use=False,
        )
        UniquePrice.objects.create(
            date=now - timedelta(days=1),
            price=Decimal('33.00'),
            unique_flip=flip_should_update,
        )

        flip_in_use = UniqueFlip.objects.create(
            unique_id='UF101',
            name='In Use',
            bought_at=now - timedelta(days=9),
            bought_price=Decimal('25.00'),
            advised_price=Decimal('40.00'),
            in_use=True,
        )
        UniquePrice.objects.create(
            date=now - timedelta(days=1),
            price=Decimal('35.00'),
            unique_flip=flip_in_use,
        )

        flip_same_price = UniqueFlip.objects.create(
            unique_id='UF102',
            name='Same Price',
            bought_at=now - timedelta(days=7),
            bought_price=Decimal('20.00'),
            advised_price=Decimal('28.00'),
            in_use=False,
        )
        UniquePrice.objects.create(
            date=now - timedelta(days=1),
            price=Decimal('28.00'),
            unique_flip=flip_same_price,
        )

        flip_no_current = UniqueFlip.objects.create(
            unique_id='UF103',
            name='No Current',
            bought_at=now - timedelta(days=6),
            bought_price=Decimal('18.00'),
            advised_price=Decimal('27.00'),
            in_use=False,
        )

        flip_sold = UniqueFlip.objects.create(
            unique_id='UF104',
            name='Sold',
            bought_at=now - timedelta(days=5),
            bought_price=Decimal('22.00'),
            advised_price=Decimal('29.00'),
            sold_at=now - timedelta(days=1),
            in_use=False,
        )
        UniquePrice.objects.create(
            date=now - timedelta(days=1),
            price=Decimal('26.00'),
            unique_flip=flip_sold,
        )

    url = reverse('altered:unique_flip_list') + '?status=current'
    user = get_user_model().objects.create_user('bulk', password='pass1234', is_staff=True)
    client.force_login(user)
    response = client.post(url, {
        'update_all_prices': '1',
    })

    assert response.status_code == 302

    flip_should_update.refresh_from_db()
    assert flip_should_update.advised_price is None
    assert flip_should_update.current_price == Decimal('35.00')

    flip_in_use.refresh_from_db()
    assert flip_in_use.advised_price == Decimal('40.00')
    assert flip_in_use.current_price == Decimal('35.00')

    flip_same_price.refresh_from_db()
    assert flip_same_price.advised_price == Decimal('28.00')
    assert flip_same_price.current_price == Decimal('28.00')

    flip_no_current.refresh_from_db()
    assert flip_no_current.advised_price == Decimal('27.00')

    flip_sold.refresh_from_db()
    assert flip_sold.advised_price == Decimal('29.00')
    assert flip_sold.current_price == Decimal('26.00')
