from datetime import date, timedelta, datetime, timezone
from typing import Sequence

from pfm_util.list_utilities.list_utilities import distance_in_list, simple_filter


def range_of_dates(start_of_range: date, end_of_range: date) -> Sequence[date]:

    # https://stackoverflow.com/a/24637447/105844

    if start_of_range <= end_of_range:
        return [
            start_of_range + timedelta(days=x)
            for x in range(0, (end_of_range - start_of_range).days + 1)
        ]
    return [
        start_of_range - timedelta(days=x)
        for x in range(0, (start_of_range - end_of_range).days + 1)
    ]


def beginning_of_week(date_: date, week_starts_on: int = 6) -> date:
    dow_index = date_.weekday()
    week_index = list(range(7))
    distance, _ = distance_in_list(
        week_index, dow_index, -1, simple_filter(week_starts_on)
    )
    if distance is not None:
        new_date = date_ - timedelta(hours=24 * distance)
        return new_date
    raise ValueError("could not find date")


def end_of_week(date_: date, week_starts_on: int = 6) -> date:
    dow_index = date_.weekday()
    week_index = list(range(7))
    distance, _ = distance_in_list(
        week_index, dow_index, 1, simple_filter(week_starts_on)
    )
    if distance == 0:
        new_date = date_ + timedelta(hours=24 * 6)
        return new_date
    if distance is not None:
        new_date = date_ + timedelta(hours=24 * (distance - 1))
        return new_date
    raise ValueError("could not find date")


def pad_to_end_of_week(date_: date) -> date:
    dow_index = 6 - date_.weekday()
    new_date = date_ + timedelta(hours=24 * dow_index)
    return new_date


def iso_date_now(tz=timezone.utc):
    return datetime.now(tz).date().isoformat()
