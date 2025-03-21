from baby_name.constants.name_choice import NameChoice
from baby_name.factories.evaluation import EvaluationFactory
from baby_name.factories.user import UserFactory
from baby_name.repositories.evaluation import EvaluationRepository


def test_get_all_positive_vote(db):
    for score in NameChoice.choices:
        EvaluationFactory.create_batch(
            3,
            score=score[0]
        )
    all_positive_votes = list(EvaluationRepository.get_all_positive_vote())
    assert len(all_positive_votes) == 6
