from the_bazaar.constants.monster import ROGUE_SCRAPPER, VIPER, BOARRIOR


class MonsterFinderService:
    MONSTERS = [
        BOARRIOR,
        ROGUE_SCRAPPER,
        VIPER,
    ]

    @classmethod
    def find_monster(cls, monster_name):
        for monster in cls.MONSTERS:
            if monster.name == monster_name:
                return monster
        raise Exception("Monster not recognized")
