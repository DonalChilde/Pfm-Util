from dataclasses import dataclass
from datetime import date, datetime, timedelta

from pfm_util.datetime_utilities.datetime_utilities import (
    beginning_of_week,
    end_of_week,
    range_of_dates,
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

    # start_of_range = datetime.today().date()
    # end_of_range = start_of_range + timedelta(days=3)
    # date_range = range_of_dates(start_of_range, end_of_range)
    # expected = [
    #     date(2019, 12, 20),
    #     date(2019, 12, 21),
    #     date(2019, 12, 22),
    #     date(2019, 12, 23),
    # ]
    # assert date_range == expected

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


def test_beginning_of_week():
    @dataclass
    class InputData:
        test_date: date
        week_starts_on: int
        expected_date: date

    test_date = date(2019, 12, 20)
    print(f"test_date {test_date}({test_date.weekday()})")
    test_data = [
        InputData(test_date, 0, date(2019, 12, 16)),
        InputData(test_date, 1, date(2019, 12, 17)),
        InputData(test_date, 2, date(2019, 12, 18)),
        InputData(test_date, 3, date(2019, 12, 19)),
        InputData(test_date, 4, date(2019, 12, 20)),
        InputData(test_date, 5, date(2019, 12, 14)),
        InputData(test_date, 6, date(2019, 12, 15)),
    ]
    for item in test_data:
        assert item.test_date.weekday() == 4
        first_day = beginning_of_week(
            date_=item.test_date, week_starts_on=item.week_starts_on
        )
        assert first_day == item.expected_date
        print(
            f"If week starts on {item.week_starts_on}, {first_day}({first_day.weekday()}) is the first day of the week for {item.test_date}({item.test_date.weekday()})"
        )
    # assert False


def test_end_of_week():
    @dataclass
    class InputData:
        test_date: date
        week_starts_on: int
        expected_date: date

    test_date = date(2019, 12, 20)
    test_data = [
        InputData(test_date, 0, date(2019, 12, 22)),
        InputData(test_date, 1, date(2019, 12, 23)),
        InputData(test_date, 2, date(2019, 12, 24)),
        InputData(test_date, 3, date(2019, 12, 25)),
        InputData(test_date, 4, date(2019, 12, 26)),
        InputData(test_date, 5, date(2019, 12, 20)),
        InputData(test_date, 6, date(2019, 12, 21)),
    ]
    print(f"test_date {test_date}({test_date.weekday()})")
    for item in test_data:
        assert item.test_date.weekday() == 4
        last_day = end_of_week(date_=item.test_date, week_starts_on=item.week_starts_on)
        assert last_day == item.expected_date
        print(
            f"If week starts on {item.week_starts_on}, {last_day}({last_day.weekday()}) is the last day of the week for {item.test_date}({item.test_date.weekday()})"
        )
    # assert False
