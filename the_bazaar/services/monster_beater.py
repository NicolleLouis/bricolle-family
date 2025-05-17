from the_bazaar.services.monster_finder import MonsterFinderService
from the_bazaar.value_objects.character import Character


class MonsterBeaterService:
    SANDSTORM_TIME = 30

    def __init__(self, player_life, player_dps=0, player_hps=0, player_pps=0, monster_name=None):
        self.player = self.generate_player(player_life, player_dps, player_hps, player_pps)
        self.opponent = self.generate_opponent(monster_name)
        self.time_to_kill = self.compute_time_to_kill()
        self.time_to_death = self.compute_time_to_death()
        self.result = self.compute()

    @staticmethod
    def generate_opponent(monster_name):
        return MonsterFinderService.find_monster(monster_name)

    @staticmethod
    def generate_player(player_life, player_dps=0, player_hps=0, player_pps=0):
        player_life = float(player_life)
        if player_dps is None:
            player_dps = 0
        else:
            player_dps = float(player_dps)
        if player_hps is None:
            player_hps = 0
        else:
            player_hps = float(player_hps)
        if player_pps is None:
            player_pps = 0
        else:
            player_pps = float(player_pps)
        return Character(
            total_life=player_life,
            dps=player_dps,
            hps=player_hps,
            pps=player_pps,
        )

    def compute(self):
        if self.time_to_death is None:
            if self.time_to_kill is None:
                return None
            else:
                return True
        else:
            if self.time_to_kill is None:
                return False
            else:
                return self.time_to_kill < self.time_to_death

    def compute_time_to_kill(self):
        return self.time_to_defeat(self.player, self.opponent)

    def compute_time_to_death(self):
        return self.time_to_defeat(self.opponent, self.player)

    @classmethod
    def time_to_defeat(cls, character, opponent):
        for time in range(60):
            damage = cls.damage_at_time(character, opponent, time)
            if damage >= opponent.total_life:
                return time
        return None

    @staticmethod
    def damage_at_time(character, opponent, time):
        poison_damage = character.pps * time ** 2 / 2
        regular_damage = character.dps * time
        soaked_damage = opponent.hps * time
        return poison_damage + regular_damage - soaked_damage

    def life_at_sandstorm(self):
        player_life = self.player.total_life - self.damage_at_time(self.opponent, self.player, self.SANDSTORM_TIME)
        opponent_life = self.opponent.total_life - self.damage_at_time(self.player, self.opponent, self.SANDSTORM_TIME)
        return player_life, opponent_life
