import factory

from baby_name.models import Name


class NameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Name

    name = factory.Faker('first_name')
    sex = factory.Faker('boolean')
