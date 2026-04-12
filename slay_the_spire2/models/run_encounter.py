from django.contrib import admin
from django.db import models


class RunEncounter(models.Model):
    class Act(models.IntegerChoices):
        ACT_1 = 0, "Act 1"
        ACT_2 = 1, "Act 2"
        ACT_3 = 2, "Act 3"

    run_summary = models.ForeignKey(
        "slay_the_spire2.RunSummary",
        on_delete=models.CASCADE,
        related_name="encounters",
    )
    encounter = models.ForeignKey(
        "slay_the_spire2.Encounter",
        on_delete=models.CASCADE,
        related_name="run_encounters",
    )
    act = models.IntegerField(choices=Act.choices)
    floor = models.IntegerField()
    damage_taken = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("run_summary", "floor", "act"),
                name="sts_unique_run_summary_floor_act",
            ),
            models.CheckConstraint(
                check=models.Q(act__in=[0, 1, 2]),
                name="sts_run_encounter_act_valid",
            )
        ]
        indexes = [
            models.Index(fields=("run_summary",), name="sts_re_run_summary_idx"),
            models.Index(fields=("encounter",), name="sts_re_encounter_idx"),
        ]

    def __str__(self):
        return f"{self.run_summary_id} - act {self.act} floor {self.floor} - {self.encounter.name} ({self.damage_taken})"


@admin.register(RunEncounter)
class RunEncounterAdmin(admin.ModelAdmin):
    list_display = ("id", "run_summary", "encounter", "act", "floor", "damage_taken")
    list_filter = ("encounter", "act")
    search_fields = ("run_summary__run_file__original_file_name", "encounter__name")
    ordering = ("-id",)
