import pytest

from capitalism.constants.object_type import ObjectType
from capitalism.models import Human, ObjectStack


@pytest.mark.django_db
def test_object_defaults():
    human = Human.objects.create(age=30)
    object_stack = ObjectStack.objects.create(owner=human)

    assert object_stack.owner == human
    assert object_stack.in_sale is False
    assert object_stack.price is None
    assert object_stack.type == ObjectType.BREAD
    assert object_stack.quantity == 1
