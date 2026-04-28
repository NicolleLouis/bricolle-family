from albion_online.templatetags.math_format import format_percent


def test_format_percent_formats_positive_negative_and_missing_values():
    assert format_percent(150) == "+150%"
    assert format_percent(12.5) == "+12.5%"
    assert format_percent(-31.25) == "-31.2%"
    assert format_percent(0) == "0%"
    assert format_percent(None) == "-"
