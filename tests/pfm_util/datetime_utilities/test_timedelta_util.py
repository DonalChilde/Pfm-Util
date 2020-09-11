from datetime import timedelta

import pytest

from pfm_util.datetime_utilities.timedelta_util import (
    HHHMMSS_to_seconds_int,
    parse_HHMMSS,
)


def test_HHHMMSS_to_seconds():
    test_value = HHHMMSS_to_seconds_int("34:10:05")
    assert test_value == (34 * 60 * 60) + (10 * 60) + 5

    test_value = HHHMMSS_to_seconds_int("34.10:05", hm_separator="\\.")
    assert test_value == (34 * 60 * 60) + (10 * 60) + 5

    test_value = HHHMMSS_to_seconds_int(
        "34+10.05", hm_separator="\\+", ms_separator="\\."
    )
    assert test_value == (34 * 60 * 60) + (10 * 60) + 5

    test_value = HHHMMSS_to_seconds_int("2334:10:05")
    assert test_value == (2334 * 60 * 60) + (10 * 60) + 5

    test_value = HHHMMSS_to_seconds_int("2334:10:05.045")
    assert test_value == (2334 * 60 * 60) + (10 * 60) + 5

    test_value = HHHMMSS_to_seconds_int("2334:10")
    assert test_value == (2334 * 60 * 60) + (10 * 60)

    test_value = HHHMMSS_to_seconds_int("00:10")
    assert test_value == (0 * 60 * 60) + (10 * 60)

    test_value = HHHMMSS_to_seconds_int("0:10")
    assert test_value == (0 * 60 * 60) + (10 * 60)

    test_value = HHHMMSS_to_seconds_int("2334:00:05")
    assert test_value == (2334 * 60 * 60) + (0 * 60) + 5

    test_value = HHHMMSS_to_seconds_int("2,334:10")
    assert test_value == (2334 * 60 * 60) + (10 * 60)

    test_value = HHHMMSS_to_seconds_int("2.334:10")
    assert test_value == (2334 * 60 * 60) + (10 * 60)

    with pytest.raises(ValueError):
        assert HHHMMSS_to_seconds_int("34:70:00")

    with pytest.raises(ValueError):
        assert HHHMMSS_to_seconds_int("34:50:70")


def test_parse_HHMMSS():
    test_value = parse_HHMMSS("34:10:05")
    assert test_value == timedelta(hours=34, minutes=10, seconds=5)

    test_value = parse_HHMMSS("34:10:05.145")
    assert test_value == timedelta(hours=34, minutes=10, seconds=5.145)

    test_value = parse_HHMMSS("34:10")
    assert test_value == timedelta(hours=34, minutes=10)

    test_value = parse_HHMMSS("2134:10:05")
    assert test_value == timedelta(hours=2134, minutes=10, seconds=5)

    test_value = parse_HHMMSS("2,134:10:05")
    assert test_value == timedelta(hours=2134, minutes=10, seconds=5)

    test_value = parse_HHMMSS("2.134:10:05")
    assert test_value == timedelta(hours=2134, minutes=10, seconds=5)

    test_value = parse_HHMMSS("34.10:05", hm_separator="\\.")
    assert test_value == timedelta(hours=34, minutes=10, seconds=5)

    test_value = parse_HHMMSS("2.134.10:05", hm_separator="\\.")
    assert test_value == timedelta(hours=2134, minutes=10, seconds=5)

    test_value = parse_HHMMSS("2.134.10:05.145", hm_separator="\\.")
    assert test_value == timedelta(hours=2134, minutes=10, seconds=5.145)

    test_value = parse_HHMMSS("34+10.05", hm_separator="\\+", ms_separator="\\.")
    assert test_value == timedelta(hours=34, minutes=10, seconds=5)

    with pytest.raises(ValueError):
        assert parse_HHMMSS("34:70:00")

    with pytest.raises(ValueError):
        assert parse_HHMMSS("34:50:70")
