from albion_online.constants.artifact_salvage import (
    ARTIFACT_SALVAGE_ARTIFACTS_BY_AODP_FRAGMENT,
    ARTIFACT_SALVAGE_ARTIFACTS_BY_LABEL,
    ARTIFACT_SALVAGE_FAMILIES,
    ARTIFACT_SALVAGE_FAMILIES_BY_KEY,
)


def _all_artifacts():
    for family in ARTIFACT_SALVAGE_FAMILIES:
        yield from family["artifacts"]


def test_artifact_salvage_families_keep_the_expected_order_and_shape():
    assert [family["key"] for family in ARTIFACT_SALVAGE_FAMILIES] == [
        "rune",
        "soul",
        "relic",
        "avalonian",
    ]
    assert [family["label"] for family in ARTIFACT_SALVAGE_FAMILIES] == [
        "Rune",
        "Soul",
        "Relic",
        "Avalonian",
    ]
    assert len(ARTIFACT_SALVAGE_FAMILIES_BY_KEY) == 4
    assert len(ARTIFACT_SALVAGE_FAMILIES_BY_KEY["rune"]["artifacts"]) == 29
    assert len(ARTIFACT_SALVAGE_FAMILIES_BY_KEY["soul"]["artifacts"]) == 29
    assert len(ARTIFACT_SALVAGE_FAMILIES_BY_KEY["relic"]["artifacts"]) == 29
    assert len(ARTIFACT_SALVAGE_FAMILIES_BY_KEY["avalonian"]["artifacts"]) == 29


def test_artifact_salvage_lookups_use_canonical_aodp_fragments():
    assert ARTIFACT_SALVAGE_ARTIFACTS_BY_LABEL["Hellish Sicklehead Pair"]["aodp_id_fragment"] == (
        "ARTEFACT_2H_TWINSCYTHE_HELL"
    )
    assert ARTIFACT_SALVAGE_ARTIFACTS_BY_LABEL["Runestone Golem Remnant"]["aodp_id_fragment"] == (
        "ARTEFACT_2H_SHAPESHIFTER_KEEPER"
    )
    assert ARTIFACT_SALVAGE_ARTIFACTS_BY_LABEL["Remnants of the Old King"]["aodp_id_fragment"] == (
        "ARTEFACT_2H_CLAYMORE_AVALON"
    )
    assert ARTIFACT_SALVAGE_ARTIFACTS_BY_AODP_FRAGMENT["ARTEFACT_MAIN_SCIMITAR_MORGANA"]["label"] == (
        "Bloodforged Blade"
    )
    assert ARTIFACT_SALVAGE_ARTIFACTS_BY_AODP_FRAGMENT["ARTEFACT_OFF_TOWERSHIELD_UNDEAD"]["label"] == (
        "Ancient Shield Core"
    )


def test_artifact_salvage_artifact_fragments_are_unique():
    fragments = [artifact["aodp_id_fragment"] for artifact in _all_artifacts()]
    assert len(fragments) == len(set(fragments))
