import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import dateutil

from pfm_util.datetime_utilities.datetime_utilities import (
    beginning_of_week,
    end_of_week,
    range_of_dates,
    tz_aware_utcnow,
)


def test_range_of_dates():
    start_date = date(2019, 1, 1)
    end_date = date(2019, 1, 5)
    date_range = range_of_dates(start_date, end_date)
    expected = [
        date(2019, 1, 1),
        date(2019, 1, 2),
        date(2019, 1, 3),
        date(2019, 1, 4),
        date(2019, 1, 5),
    ]
    assert date_range == expected

    start_date = date(2019, 1, 5)
    end_date = date(2019, 1, 1)
    date_range = range_of_dates(start_date, end_date)
    expected = [
        date(2019, 1, 5),
        date(2019, 1, 4),
        date(2019, 1, 3),
        date(2019, 1, 2),
        date(2019, 1, 1),
    ]
    assert date_range == expected

    start_date = date(2019, 1, 1)
    end_date = date(2019, 1, 1)
    date_range = range_of_dates(start_date, end_date)
    expected = [date(2019, 1, 1)]
    assert date_range == expected

    start_date = datetime.today().date()
    end_date = start_date + timedelta(days=5)
    date_range = range_of_dates(start_date, end_date)
    expected = [
        start_date,
        start_date + timedelta(days=1),
        start_date + timedelta(days=2),
        start_date + timedelta(days=3),
        start_date + timedelta(days=4),
        start_date + timedelta(days=5),
    ]
    assert date_range == expected

    start_of_range = datetime.today().date()
    end_of_range = start_of_range - timedelta(days=3)
    date_range = range_of_dates(start_of_range, end_of_range)
    expected = [
        start_date,
        start_date - timedelta(days=1),
        start_date - timedelta(days=2),
        start_date - timedelta(days=3),
    ]
    assert date_range == expected


def test_beginning_of_week(caplog):
    caplog.set_level(logging.DEBUG)

    @dataclass
    class InputData:
        test_date: date
        week_starts_on: int
        expected_date: date
        iso: bool

    test_date = date(2019, 12, 20)  # Friday
    logging.debug("test_date %s(%s)", test_date, test_date.strftime("%a"))
    test_data = [
        InputData(test_date, 0, date(2019, 12, 16), False),
        InputData(test_date, 1, date(2019, 12, 17), False),
        InputData(test_date, 2, date(2019, 12, 18), False),
        InputData(test_date, 3, date(2019, 12, 19), False),
        InputData(test_date, 4, date(2019, 12, 20), False),
        InputData(test_date, 5, date(2019, 12, 14), False),
        InputData(test_date, 6, date(2019, 12, 15), False),
        InputData(test_date, 1, date(2019, 12, 16), True),
        InputData(test_date, 2, date(2019, 12, 17), True),
        InputData(test_date, 3, date(2019, 12, 18), True),
        InputData(test_date, 4, date(2019, 12, 19), True),
        InputData(test_date, 5, date(2019, 12, 20), True),
        InputData(test_date, 6, date(2019, 12, 14), True),
        InputData(test_date, 7, date(2019, 12, 15), True),
    ]

    for item in test_data:
        assert item.test_date.weekday() == 4
        assert item.test_date.isoweekday() == 5
        first_day = beginning_of_week(
            date_=item.test_date, week_starts_on=item.week_starts_on, iso=item.iso
        )
        assert first_day == item.expected_date
        if item.iso:
            logging.debug(
                "If week starts on %s, %s(index: %s, %s) is the first day of the week for %s(index: %s, %s)",
                item.week_starts_on,
                first_day,
                first_day.isoweekday(),
                first_day.strftime("%a"),
                item.test_date,
                item.test_date.isoweekday(),
                item.test_date.strftime("%a"),
            )
        else:
            logging.debug(
                "If week starts on %s, %s(index: %s, %s) is the first day of the week for %s(index: %s, %s)",
                item.week_starts_on,
                first_day,
                first_day.weekday(),
                first_day.strftime("%a"),
                item.test_date,
                item.test_date.weekday(),
                item.test_date.strftime("%a"),
            )


def test_end_of_week(caplog):
    caplog.set_level(logging.DEBUG)

    @dataclass
    class InputData:
        test_date: date
        week_starts_on: int
        expected_date: date
        iso: bool

    test_date = date(2019, 12, 20)  # Friday
    logging.debug("test_date %s(%s)", test_date, test_date.strftime("%a"))
    test_data = [
        InputData(test_date, 0, date(2019, 12, 22), False),
        InputData(test_date, 1, date(2019, 12, 23), False),
        InputData(test_date, 2, date(2019, 12, 24), False),
        InputData(test_date, 3, date(2019, 12, 25), False),
        InputData(test_date, 4, date(2019, 12, 26), False),
        InputData(test_date, 5, date(2019, 12, 20), False),
        InputData(test_date, 6, date(2019, 12, 21), False),
        InputData(test_date, 1, date(2019, 12, 22), True),
        InputData(test_date, 2, date(2019, 12, 23), True),
        InputData(test_date, 3, date(2019, 12, 24), True),
        InputData(test_date, 4, date(2019, 12, 25), True),
        InputData(test_date, 5, date(2019, 12, 26), True),
        InputData(test_date, 6, date(2019, 12, 20), True),
        InputData(test_date, 7, date(2019, 12, 21), True),
    ]
    for item in test_data:
        assert item.test_date.weekday() == 4
        assert item.test_date.isoweekday() == 5
        last_day = end_of_week(
            date_=item.test_date, week_starts_on=item.week_starts_on, iso=item.iso
        )
        assert last_day == item.expected_date
        if item.iso:
            logging.debug(
                "If week starts on %s, %s(index: %s, %s) is the last day of the week for %s(index: %s, %s)",
                item.week_starts_on,
                last_day,
                last_day.isoweekday(),
                last_day.strftime("%a"),
                item.test_date,
                item.test_date.isoweekday(),
                item.test_date.strftime("%a"),
            )
        else:
            logging.debug(
                "If week starts on %s, %s(index: %s, %s) is the last day of the week for %s(index: %s, %s)",
                item.week_starts_on,
                last_day,
                last_day.weekday(),
                last_day.strftime("%a"),
                item.test_date,
                item.test_date.weekday(),
                item.test_date.strftime("%a"),
            )


def test_tz_aware_utcnow(caplog):
    caplog.set_level(logging.DEBUG)
    result = tz_aware_utcnow()
    logging.debug(
        "UTC now with time zone: %s, without time zone: %s", result, datetime.utcnow()
    )
    assert result.tzinfo == dateutil.tz.UTC
