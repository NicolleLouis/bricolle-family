class RogueScrapperBeater:
    ROGUE_SCRAPPER_LIFE = 450
    ROGUE_SCRAPPER_SHIELD = 60
    ROGUE_SCRAPPER_DPS = 9.5
    ROGUE_SCRAPPER_HPS = 7.5

    def __init__(self, player_life, player_dps = 0, player_hps = 0):
        self.player_life = player_life
        self.player_dps = player_dps
        self.player_hps = player_hps
        self.sanitize()
        self.result = self.compute()

    def sanitize(self):
        self.player_life = float(self.player_life)
        if self.player_dps is None:
            self.player_dps = 0
        else:
            self.player_dps = float(self.player_dps)
        if self.player_hps is None:
            self.player_hps = 0
        else:
            self.player_hps = float(self.player_hps)

    def compute(self):
        time_to_death = self.compute_time_to_death()
        time_to_kill = self.compute_time_to_kill()

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

    def compute_time_to_kill(self):
        rogue_scrapper_total_life = self.ROGUE_SCRAPPER_SHIELD + self.ROGUE_SCRAPPER_LIFE
        relative_dps = self.player_dps - self.ROGUE_SCRAPPER_HPS
        if relative_dps <= 0:
            return None
        else:
            return rogue_scrapper_total_life / relative_dps

    def compute_time_to_death(self):
        relative_dps = self.ROGUE_SCRAPPER_DPS - self.player_hps
        if relative_dps <= 0:
            return None
        else:
            return self.player_life / relative_dps
