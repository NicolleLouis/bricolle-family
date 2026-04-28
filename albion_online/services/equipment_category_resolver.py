from albion_online.constants.equipment_category import EquipmentCategory


class EquipmentCategoryResolver:
    def resolve(self, object_type: str) -> str | None:
        equipment_categories_by_type = {
            "ARMOR": EquipmentCategory.CHEST,
            "OFF": EquipmentCategory.OFFHAND,
            "MAIN": EquipmentCategory.SINGLE_HAND,
            "2H": EquipmentCategory.TWO_HAND,
            "SHOES": EquipmentCategory.SHOE,
        }
        return equipment_categories_by_type.get(object_type)
