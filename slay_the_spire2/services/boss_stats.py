from django.db.models import Avg

from slay_the_spire2.models.encounter import Encounter
from slay_the_spire2.models.run_encounter import RunEncounter


class BossStatsService:
    def get_boss_dangerousness_stats(
        self,
        character_id: int | None = None,
        act: int | None = None,
    ) -> list[dict]:
        encounter_rows = RunEncounter.objects.filter(
            encounter__type=Encounter.Type.BOSS,
        )
        if character_id is not None:
            encounter_rows = encounter_rows.filter(run_summary__character_id=character_id)
        if act is not None:
            encounter_rows = encounter_rows.filter(act=act)

        rows = (
            encounter_rows.values("encounter__name")
            .annotate(
                average_damage_taken=Avg("damage_taken"),
            )
            .order_by("-average_damage_taken", "encounter__name")
        )

        return [
            {
                "encounter_name": row["encounter__name"],
                "average_damage_taken": round(row["average_damage_taken"] or 0.0, 2),
            }
            for row in rows
        ]
