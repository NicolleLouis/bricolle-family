from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone

from altered.models import UniqueFlip, UniquePrice
from altered.views.unique_flip import _filter_flips


@pytest.mark.django_db
def test_unique_flip_price_issue_toggle_filters_results():
    now = timezone.now()

    with patch('altered.signals.AlteredFetchUniqueDataService') as mocked_service:
        mocked_service.return_value.handle.return_value = None

        flip_without_price = UniqueFlip.objects.create(
            unique_id='UF001',
            bought_at=now,
            bought_price=Decimal('10.00'),
            name='Without Price',
        )

        flip_up_to_date = UniqueFlip.objects.create(
            unique_id='UF002',
            bought_at=now,
            bought_price=Decimal('12.00'),
            name='Up To Date',
        )
        UniquePrice.objects.create(
            date=now,
            price=Decimal('15.00'),
            unique_flip=flip_up_to_date,
        )

        flip_needs_update = UniqueFlip.objects.create(
            unique_id='UF003',
            bought_at=now,
            bought_price=Decimal('8.00'),
            advised_price=Decimal('20.00'),
            name='Needs Update',
        )
        UniquePrice.objects.create(
            date=now,
            price=Decimal('18.00'),
            unique_flip=flip_needs_update,
        )

    queryset = UniqueFlip.objects.all()
    filtered_ids = set(
        _filter_flips(
            queryset,
            status='current',
            faction=None,
            hide_zero=False,
            price_issues_only=True,
        ).values_list('unique_id', flat=True)
    )
    assert filtered_ids == {flip_without_price.unique_id, flip_needs_update.unique_id}

    all_ids = set(
        _filter_flips(
            queryset,
            status='current',
            faction=None,
            hide_zero=False,
            price_issues_only=False,
        ).values_list('unique_id', flat=True)
    )
    assert all_ids == {
        flip_without_price.unique_id,
        flip_up_to_date.unique_id,
        flip_needs_update.unique_id,
    }
