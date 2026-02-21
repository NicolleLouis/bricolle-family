from dataclasses import dataclass

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models.functions import Lower

from baby_name.constants.name_choice import NameChoice
from baby_name.models import Evaluation, Name
from baby_name.services.mass_yes_name_parser import MassYesNameParser
from core.models import Family


@dataclass
class MassYesResult:
    parsed_names: list[str]
    created_name_count: int
    created_evaluation_count: int
    updated_evaluation_count: int
    unchanged_positive_count: int


class MassYesService:
    def execute(self, raw_names: str, family: Family, source_name: str) -> MassYesResult:
        parsed_names = MassYesNameParser().parse_names(raw_names)
        if not parsed_names:
            return MassYesResult(
                parsed_names=[],
                created_name_count=0,
                created_evaluation_count=0,
                updated_evaluation_count=0,
                unchanged_positive_count=0,
            )

        with transaction.atomic():
            family_users = list(self._get_family_users(family))
            names, created_name_count = self._get_or_create_names(parsed_names, source_name)
            evaluation_by_key = self._get_existing_evaluations(family_users, names)

            created_evaluation_count = 0
            updated_evaluation_count = 0
            unchanged_positive_count = 0

            for user in family_users:
                for name in names:
                    evaluation_key = (user.id, name.id)
                    evaluation = evaluation_by_key.get(evaluation_key)

                    if evaluation is None:
                        Evaluation.objects.create(user=user, name=name, score=NameChoice.OUI.value)
                        created_evaluation_count += 1
                        continue

                    if evaluation.score == NameChoice.NON.value:
                        evaluation.score = NameChoice.OUI.value
                        evaluation.save(update_fields=["score"])
                        updated_evaluation_count += 1
                        continue

                    if evaluation.score in [NameChoice.OUI.value, NameChoice.COUP_DE_COEUR.value]:
                        unchanged_positive_count += 1

        return MassYesResult(
            parsed_names=parsed_names,
            created_name_count=created_name_count,
            created_evaluation_count=created_evaluation_count,
            updated_evaluation_count=updated_evaluation_count,
            unchanged_positive_count=unchanged_positive_count,
        )

    def _get_family_users(self, family: Family):
        return User.objects.filter(userprofile__family=family)

    def _get_or_create_names(self, parsed_names: list[str], source_name: str) -> tuple[list[Name], int]:
        lowercase_names = [name.lower() for name in parsed_names]
        existing_names = (
            Name.objects.annotate(lower_name=Lower("name"))
            .filter(lower_name__in=lowercase_names)
            .order_by("id")
        )
        existing_by_lower_name: dict[str, Name] = {}
        for name in existing_names:
            if name.lower_name not in existing_by_lower_name:
                existing_by_lower_name[name.lower_name] = name

        names: list[Name] = []
        created_name_count = 0
        for parsed_name in parsed_names:
            lowercase_name = parsed_name.lower()
            existing_name = existing_by_lower_name.get(lowercase_name)
            if existing_name:
                names.append(existing_name)
                continue

            created_name = Name.objects.create(
                name=parsed_name,
                sex=False,
                source=source_name,
                tag="mass_yes",
            )
            created_name_count += 1
            existing_by_lower_name[lowercase_name] = created_name
            names.append(created_name)

        return names, created_name_count

    def _get_existing_evaluations(self, users: list[User], names: list[Name]) -> dict[tuple[int, int], Evaluation]:
        evaluations = Evaluation.objects.filter(user__in=users, name__in=names)
        evaluation_by_key: dict[tuple[int, int], Evaluation] = {}
        for evaluation in evaluations:
            evaluation_by_key[(evaluation.user_id, evaluation.name_id)] = evaluation
        return evaluation_by_key
