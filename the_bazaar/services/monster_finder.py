from the_bazaar.constants.monster import ROGUE_SCRAPPER


class MonsterFinderService:
    MONSTERS = [
        ROGUE_SCRAPPER,
    ]

    @classmethod
    def find_monster(cls, monster_name):
        for monster in cls.MONSTERS:
            if monster.name == monster_name:
                return monster
        raise Exception("Monster not recognized")