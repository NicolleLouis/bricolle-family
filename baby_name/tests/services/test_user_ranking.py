import random

from baby_name.factories.evaluation import EvaluationFactory
from baby_name.factories.name import NameFactory
from baby_name.factories.user import UserFactory
from baby_name.services.user_ranking import UserRanking


def test_get_name_position(db):
    sex = random.choice([True, False])
    name_1 = NameFactory(sex=sex)
    name_2 = NameFactory(sex=sex)
    name_3 = NameFactory(sex=sex)
    user = UserFactory()
    EvaluationFactory(
        name=name_1,
        user=user,
        elo=900
    )
    EvaluationFactory(
        name=name_2,
        user=user,
        elo=1000
    )
    EvaluationFactory(
        name=name_3,
        user=user,
        elo=1100
    )
    assert UserRanking.get_name_position(user=user, name=name_1) == 3
    assert UserRanking.get_name_position(user=user, name=name_2) == 2
    assert UserRanking.get_name_position(user=user, name=name_3) == 1