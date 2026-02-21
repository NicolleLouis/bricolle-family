from baby_name.constants.name_choice import NameChoice
from baby_name.models import Evaluation, Name
from baby_name.services.mass_yes import MassYesService
from baby_name.factories.user import UserFactory
from core.models import Family


def test_execute_creates_missing_names_and_missing_evaluations(db):
    family = Family.objects.create(name="Bricolle")
    first_user = UserFactory()
    second_user = UserFactory()
    first_user.userprofile.family = family
    first_user.userprofile.save()
    second_user.userprofile.family = family
    second_user.userprofile.save()

    result = MassYesService().execute(
        raw_names="Alice\nBob",
        family=family,
        source_name="mass_script",
        sex=True,
    )

    assert result.created_name_count == 2
    assert result.created_evaluation_count == 4
    assert result.updated_evaluation_count == 0

    assert Name.objects.filter(name="Alice", sex=True).exists()
    assert Name.objects.filter(name="Bob", sex=True).exists()
    assert Evaluation.objects.filter(score=NameChoice.OUI.value).count() == 4


def test_execute_updates_only_non_evaluations_and_keeps_positive_ones(db):
    family = Family.objects.create(name="Bricolle")
    first_user = UserFactory()
    second_user = UserFactory()
    first_user.userprofile.family = family
    first_user.userprofile.save()
    second_user.userprofile.family = family
    second_user.userprofile.save()

    alice = Name.objects.create(name="Alice", sex=False, source="seed")
    Evaluation.objects.create(user=first_user, name=alice, score=NameChoice.NON.value)
    Evaluation.objects.create(user=second_user, name=alice, score=NameChoice.OUI.value)

    result = MassYesService().execute(
        raw_names="Alice",
        family=family,
        source_name="mass_script",
        sex=False,
    )

    first_evaluation = Evaluation.objects.get(user=first_user, name=alice)
    second_evaluation = Evaluation.objects.get(user=second_user, name=alice)

    assert result.created_name_count == 0
    assert result.created_evaluation_count == 0
    assert result.updated_evaluation_count == 1
    assert result.unchanged_positive_count == 1

    assert first_evaluation.score == NameChoice.OUI.value
    assert second_evaluation.score == NameChoice.OUI.value


def test_execute_does_not_mix_same_name_between_boy_and_girl(db):
    family = Family.objects.create(name="Bricolle")
    first_user = UserFactory()
    second_user = UserFactory()
    first_user.userprofile.family = family
    first_user.userprofile.save()
    second_user.userprofile.family = family
    second_user.userprofile.save()

    existing_name = Name.objects.create(name="Camille", sex=False, source="seed")

    result = MassYesService().execute(
        raw_names="Camille",
        family=family,
        source_name="mass_script",
        sex=True,
    )

    assert result.created_name_count == 1
    assert Name.objects.filter(name="Camille", sex=False).count() == 1
    assert Name.objects.filter(name="Camille", sex=True).count() == 1
    assert Evaluation.objects.filter(name=existing_name).count() == 0
