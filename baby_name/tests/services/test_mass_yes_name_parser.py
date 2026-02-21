from baby_name.services.mass_yes_name_parser import MassYesNameParser


def test_parse_names_splits_and_trims_names():
    parser = MassYesNameParser()

    result = parser.parse_names("Alice, Bob\n Charly ;  Diane  ")

    assert result == ["Alice", "Bob", "Charly", "Diane"]


def test_parse_names_removes_case_insensitive_duplicates_and_empty_values():
    parser = MassYesNameParser()

    result = parser.parse_names("Alice\nalice\n  \nALICE ; Bob")

    assert result == ["Alice", "Bob"]
