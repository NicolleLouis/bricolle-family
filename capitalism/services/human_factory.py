from faker import Faker
from django.apps import apps

from capitalism.constants.simulation_step import SimulationStep


class HumanFactory:
    faker = Faker("fr_FR")

    @staticmethod
    def _model():
        return apps.get_model("capitalism", "Human")

    @classmethod
    def create(cls, job):
        Human = cls._model()
        return Human.objects.create(
            name=cls.faker.name(),
            job=job,
            step=SimulationStep.START_OF_DAY,
            dead=False,
            time_since_need_fulfilled=0,
            time_without_full_needs=0,
        )

    @classmethod
    def bulk_create(cls, job, amount):
        Human = cls._model()
        humans = [
            Human(
                name=cls.faker.name(),
                job=job,
                step=SimulationStep.START_OF_DAY,
                dead=False,
                time_since_need_fulfilled=0,
                time_without_full_needs=0,
            )
            for _ in range(amount)
        ]
        Human.objects.bulk_create(humans)
        return humans
