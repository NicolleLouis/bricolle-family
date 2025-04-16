class RogueScrapperBeater:
    ROGUE_SCRAPPER_LIFE = 450
    ROGUE_SCRAPPER_SHIELD = 60
    ROGUE_SCRAPPER_DPS = 9.5
    ROGUE_SCRAPPER_HPS = 7.5

    @classmethod
    def compute(cls, player_life, player_dps = 0, player_hps = 0):
        time_to_death = cls.compute_time_to_death(player_life, player_hps)
        time_to_kill = cls.compute_time_to_kill(player_dps)

        if time_to_death is None:
            if time_to_kill is None:
                return None
            else:
                return True
        else:
            if time_to_kill is None:
                return False
            else:
                return time_to_kill < time_to_death

    @classmethod
    def compute_time_to_kill(cls, player_dps = 0):
        rogue_scrapper_total_life = cls.ROGUE_SCRAPPER_SHIELD + cls.ROGUE_SCRAPPER_LIFE
        relative_dps = float(player_dps) - cls.ROGUE_SCRAPPER_HPS
        if relative_dps <= 0:
            return None
        else:
            return rogue_scrapper_total_life / relative_dps

    @classmethod
    def compute_time_to_death(cls, player_life = 0, player_hps = 0):
        relative_dps = cls.ROGUE_SCRAPPER_DPS - float(player_hps)
        if relative_dps <= 0:
            return None
        else:
            return player_life / relative_dps
