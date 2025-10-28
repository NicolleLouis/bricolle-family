import pytest

from capitalism.constants.object_type import ObjectType
from capitalism.models import Human, Object


@pytest.mark.django_db
def test_object_defaults():
    human = Human.objects.create(age=30)
    obj = Object.objects.create(owner=human)

    assert obj.owner == human
    assert obj.in_sale is False
    assert obj.price is None
    assert obj.type == ObjectType.BREAD
