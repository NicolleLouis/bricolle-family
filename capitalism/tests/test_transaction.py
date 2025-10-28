import pytest

from capitalism.constants.object_type import ObjectType
from capitalism.models import Transaction


@pytest.mark.django_db
def test_transaction_creation():
    txn = Transaction.objects.create(object_type=ObjectType.ORE, price=150)

    assert txn.object_type == ObjectType.ORE
    assert txn.price == 150
