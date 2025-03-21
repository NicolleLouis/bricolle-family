import factory

from baby_name.constants.name_choice import NameChoice
from baby_name.factories.name import NameFactory
from baby_name.factories.user import UserFactory
from baby_name.models import Evaluation


class EvaluationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Evaluation

    name = factory.SubFactory(NameFactory)
    user = factory.SubFactory(UserFactory)
    score = factory.Faker('random_element', elements=NameChoice.choices)
