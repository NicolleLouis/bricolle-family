import pytest

from capitalism.constants.object_type import ObjectType
from capitalism.models import Transaction
from capitalism.services.transactions import TransactionListingService


@pytest.mark.django_db
def test_transaction_listing_service_returns_all_transactions_by_default():
    first = Transaction.objects.create(object_type=ObjectType.WOOD, price=5)
    second = Transaction.objects.create(object_type=ObjectType.BREAD, price=7)

    context = TransactionListingService().run()

    transactions = list(context["transactions"])
    assert transactions == [second, first]
    assert context["selected_object_type"] is None
    assert ObjectType.BREAD in dict(context["object_types"])


@pytest.mark.django_db
def test_transaction_listing_service_filters_by_object_type():
    Transaction.objects.create(object_type=ObjectType.WOOD, price=5)
    bread_transaction = Transaction.objects.create(object_type=ObjectType.BREAD, price=7)

    context = TransactionListingService(object_type=ObjectType.BREAD).run()

    transactions = list(context["transactions"])
    assert transactions == [bread_transaction]
    assert context["selected_object_type"] == ObjectType.BREAD
