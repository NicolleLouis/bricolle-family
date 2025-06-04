import factory

from baby_name.models import Name


class NameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Name

    name = factory.Sequence(lambda n: f"Name{n}")
    sex = factory.Faker('boolean')
