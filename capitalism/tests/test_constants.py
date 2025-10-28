from capitalism.constants import BASE_NEEDS, ObjectType


def test_base_needs_contents():
    assert BASE_NEEDS == (
        (ObjectType.WOOD, 1),
        (ObjectType.BREAD, 1),
    )
