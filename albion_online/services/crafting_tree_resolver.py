from albion_online.constants.crafting_tree import CraftingTree


class CraftingTreeResolver:
    _armor_material_by_token = {
        "CLOTH": "cloth",
        "LEATHER": "leather",
        "PLATE": "metal",
    }
    _armor_slot_by_type = {
        "HEAD": "head",
        "ARMOR": "chest",
        "SHOES": "shoe",
    }
    _weapon_patterns = (
        ("SHAPESHIFTER", CraftingTree.SHAPESHIFTER_STAFF),
        ("NATURESTAFF", CraftingTree.NATURE_STAFF),
        ("WILDSTAFF", CraftingTree.NATURE_STAFF),
        ("CURSEDSTAFF", CraftingTree.CURSED_STAFF),
        ("DEMONICSTAFF", CraftingTree.CURSED_STAFF),
        ("SKULLORB", CraftingTree.CURSED_STAFF),
        ("ARCANESTAFF", CraftingTree.ARCANE_STAFF),
        ("ENIGMATICSTAFF", CraftingTree.ARCANE_STAFF),
        ("ENIGMATICORB", CraftingTree.ARCANE_STAFF),
        ("ARCANE", CraftingTree.ARCANE_STAFF),
        ("HOLYSTAFF", CraftingTree.HOLY_STAFF),
        ("DIVINESTAFF", CraftingTree.HOLY_STAFF),
        ("FIRESTAFF", CraftingTree.FIRE_STAFF),
        ("INFERNOSTAFF", CraftingTree.FIRE_STAFF),
        ("FIRE", CraftingTree.FIRE_STAFF),
        ("FROSTSTAFF", CraftingTree.FROST_STAFF),
        ("GLACIALSTAFF", CraftingTree.FROST_STAFF),
        ("ICEGAUNTLETS", CraftingTree.FROST_STAFF),
        ("ICECRYSTAL", CraftingTree.FROST_STAFF),
        ("QUARTERSTAFF", CraftingTree.QUARTERSTAFF),
        ("DOUBLEBLADEDSTAFF", CraftingTree.QUARTERSTAFF),
        ("IRONCLADEDSTAFF", CraftingTree.QUARTERSTAFF),
        ("COMBATSTAFF", CraftingTree.QUARTERSTAFF),
        ("ROCKSTAFF", CraftingTree.QUARTERSTAFF),
        ("KNUCKLES", CraftingTree.KNUCKLES),
        ("GAUNTLETS", CraftingTree.KNUCKLES),
        ("CROSSBOW", CraftingTree.CROSSBOW),
        ("BOW", CraftingTree.BOW),
        ("DAGGER", CraftingTree.DAGGER),
        ("CLAW", CraftingTree.DAGGER),
        ("SICKLE", CraftingTree.DAGGER),
        ("KATAR", CraftingTree.DAGGER),
        ("SPEAR", CraftingTree.SPEAR),
        ("GLAIVE", CraftingTree.SPEAR),
        ("HARPOON", CraftingTree.SPEAR),
        ("TRIDENT", CraftingTree.SPEAR),
        ("AXE", CraftingTree.AXE),
        ("SCYTHE", CraftingTree.AXE),
        ("CLEAVER", CraftingTree.AXE),
        ("SWORD", CraftingTree.SWORD),
        ("CLAYMORE", CraftingTree.SWORD),
        ("SCIMITAR", CraftingTree.SWORD),
        ("RAPIER", CraftingTree.SWORD),
        ("MACE", CraftingTree.MACE),
        ("FLAIL", CraftingTree.MACE),
        ("HAMMER", CraftingTree.HAMMER),
        ("RAM", CraftingTree.HAMMER),
    )
    _offhand_patterns = (
        ("SHIELD", CraftingTree.SHIELD),
        ("TOTEM", CraftingTree.SHIELD),
        ("BOOK", CraftingTree.BOOK),
        ("TOME", CraftingTree.BOOK),
        ("LAMP", CraftingTree.BOOK),
        ("ORB", CraftingTree.ORB),
        ("SKULL", CraftingTree.ORB),
        ("TORCH", CraftingTree.TORCH),
        ("CENSER", CraftingTree.CENSER),
        ("HORN", CraftingTree.HORN),
        ("TALISMAN", CraftingTree.TALISMAN),
        ("JESTERCANE", CraftingTree.TALISMAN),
    )

    def resolve(self, aodp_id: str) -> str | None:
        normalized_aodp_id = self._normalize_aodp_id(aodp_id)
        parts = normalized_aodp_id.split("_")
        if len(parts) < 2:
            return None

        object_type = parts[1] if parts[0].startswith("T") and parts[0][1:].isdigit() else parts[0]
        object_payload = "_".join(parts[2:]) if object_type != parts[0] else "_".join(parts[1:])

        if object_type in self._armor_slot_by_type:
            return self._resolve_armor(object_type, parts)
        if object_type in {"MAIN", "2H"}:
            return self._resolve_from_patterns(object_payload, self._weapon_patterns)
        if object_type == "OFF":
            return self._resolve_from_patterns(object_payload, self._offhand_patterns)
        return None

    def _normalize_aodp_id(self, aodp_id: str) -> str:
        return aodp_id.split("@", 1)[0]

    def _resolve_armor(self, object_type: str, parts: list[str]) -> str | None:
        slot = self._armor_slot_by_type[object_type]
        if len(parts) < 3:
            return None

        material_token = parts[2]
        material = self._armor_material_by_token.get(material_token)
        if material is not None:
            return f"{material}_{slot}"

        if material_token == "GATHERER" and len(parts) >= 4:
            return f"gatherer_{parts[3].lower()}_{slot}"

        return None

    def _resolve_from_patterns(self, payload: str, patterns: tuple[tuple[str, str], ...]) -> str | None:
        for pattern, crafting_tree in patterns:
            if pattern in payload:
                return crafting_tree
        return None
