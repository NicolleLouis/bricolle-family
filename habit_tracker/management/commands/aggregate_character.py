from django.core.management.base import BaseCommand
from habit_tracker.constants.bazaar.character import Character
from habit_tracker.services.bazaar_aggregate_character_run import BazaarAggregateCharacterRunService


class Command(BaseCommand):
    help = "Calcule les statistiques agrégées pour tous les personnages du bazar."

    def handle(self, *args, **kwargs):
        self.stdout.write("Calcul des statistiques agrégées pour chaque personnage...\n")
        for character in Character.values:
            service = BazaarAggregateCharacterRunService(character=character)
            result = service.result
            self.stdout.write(f"Personnage : {result.character}\n")
            self.stdout.write(f"  - Nombre de run: {len(service.runs)}\n")
            self.stdout.write(f"  - Victoire moyenne : {result.average_victory_number}\n")
            self.stdout.write(f"  - Meilleur résultat : {result.best_result}\n")
            self.stdout.write(f"  - Changement d'ELO : {result.elo_change}\n")
            self.stdout.write(f"  - Runs cette saison : {result.run_this_season}\n")
        self.stdout.write("Statistiques calculées avec succès.\n")
