import random

from baby_name.constants.name_choice import NameChoice
from baby_name.factories.evaluation import EvaluationFactory
from baby_name.factories.name import NameFactory
from baby_name.factories.user import UserFactory
from baby_name.repositories.name import NameRepository


def test_get_all_positives(db):
    sex = random.choice([True, False])
    name_1 = NameFactory(
        sex=sex
    )
    name_2 = NameFactory(
        sex=sex
    )
    name_3 = NameFactory(
        sex=sex
    )
    EvaluationFactory(
        name=name_1,
        score=NameChoice.NON.value
    )
    EvaluationFactory(
        name=name_2,
        score=NameChoice.OUI.value
    )
    EvaluationFactory(
        name=name_3,
        score=NameChoice.COUP_DE_COEUR.value
    )
    expected_names = [name_2, name_3]
    all_names_with_positive_vote = NameRepository.get_all_family_positive(sex=sex)
    assert len(expected_names) == len(all_names_with_positive_vote)
    for expected_name in expected_names:
        assert expected_name in all_names_with_positive_vote


def test_get_all_rankables_per_user_case_solo_user(db):
    user = UserFactory()
    sex = random.choice([True, False])
    name_1 = NameFactory(
        sex=sex
    )
    name_2 = NameFactory(
        sex=sex
    )
    name_3 = NameFactory(
        sex=sex
    )
    EvaluationFactory(
        user=user,
        name=name_1,
        score=NameChoice.NON.value
    )
    EvaluationFactory(
        user=user,
        name=name_2,
        score=NameChoice.OUI.value
    )
    EvaluationFactory(
        user=user,
        name=name_3,
        score=NameChoice.COUP_DE_COEUR.value
    )
    expected_names = [name_2, name_3]
    rankable_names = NameRepository.get_all_rankables_per_user(sex=sex, user=user)
    assert len(expected_names) == len(rankable_names)
    for expected_name in expected_names:
        assert expected_name in rankable_names


def test_get_all_rankables_per_user_case_another_user_linked_name(db):
    user_1 = UserFactory()
    user_2 = UserFactory()
    sex = random.choice([True, False])
    name = NameFactory(
        sex=sex
    )
    EvaluationFactory(
        user=user_1,
        name=name,
        score=NameChoice.NON.value
    )
    EvaluationFactory(
        user=user_2,
        name=name,
        score=NameChoice.OUI.value
    )
    rankable_names = NameRepository.get_all_rankables_per_user(sex=sex, user=user_1)
    assert len(rankable_names) == 1
    assert rankable_names[0] == name


def test_get_all_rankables_case_name_unranked(db):
    user_1 = UserFactory()
    user_2 = UserFactory()
    sex = random.choice([True, False])
    name = NameFactory(
        sex=sex
    )
    EvaluationFactory(
        user=user_2,
        name=name,
        score=NameChoice.OUI.value
    )
    rankable_names = NameRepository.get_all_rankables_per_user(sex=sex, user=user_1)
    assert len(rankable_names) == 0


def test_get_priority_score_case_name_unranked(db):
    user_1 = UserFactory()
    user_2 = UserFactory()
    sex = random.choice([True, False])
    name = NameFactory(
        sex=sex
    )
    EvaluationFactory(
        user=user_2,
        name=name,
        score=NameChoice.OUI.value
    )
    rankable_names = NameRepository.get_priority_to_score(sex=sex, user=user_1)
    assert len(rankable_names) == 1


def test_get_priority_score_case_name_already_ranked(db):
    user_1 = UserFactory()
    user_2 = UserFactory()
    sex = random.choice([True, False])
    name = NameFactory(
        sex=sex
    )
    EvaluationFactory(
        user=user_1,
        name=name,
        score=NameChoice.OUI.value
    )
    EvaluationFactory(
        user=user_2,
        name=name,
        score=NameChoice.OUI.value
    )
    priority_names = NameRepository.get_priority_to_score(sex=sex, user=user_1)
    assert len(priority_names) == 0


def test_get_all_globally_evaluated_case_missing_evaluation(db):
    sex = random.choice([True, False])
    user_1 = UserFactory()
    UserFactory()
    name = NameFactory(sex=sex)
    EvaluationFactory(
        user=user_1,
        name=name
    )
    result = NameRepository.get_all_positives_in_family(sex)
    assert len(result) == 0


def test_get_all_globally_evaluated_case_complete(db):
    sex = random.choice([True, False])
    users = UserFactory.create_batch(2)
    name = NameFactory(sex=sex)
    for user in users:
        EvaluationFactory(
            name=name,
            user=user,
            score=NameChoice.OUI.value
        )
    result = NameRepository.get_all_positives_in_family(sex)
    assert len(result) == 1
    assert result[0] == name
