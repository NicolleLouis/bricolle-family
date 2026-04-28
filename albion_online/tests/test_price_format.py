from albion_online.templatetags.price_format import compact_price


def test_compact_price_formats_thousands_millions_and_billions():
    assert compact_price(999) == "999"
    assert compact_price(1_000) == "1k"
    assert compact_price(1_250) == "1.2k"
    assert compact_price(1_000_000) == "1M"
    assert compact_price(1_750_000) == "1.8M"
    assert compact_price(1_000_000_000) == "1B"
    assert compact_price(1_250_000_000) == "1.2B"


def test_compact_price_preserves_sign_and_handles_none():
    assert compact_price(-1_250) == "-1.2k"
    assert compact_price(None) == "-"
