import logging
from datetime import date, datetime, timedelta, timezone
from typing import Sequence

from dateutil import tz

from pfm_util.list_utilities.list_utilities import distance_in_list, simple_filter

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def range_of_dates(start_of_range: date, end_of_range: date) -> Sequence[date]:
    """
    Creates a list of dates between a start and end date, inclusive.

    [extended_summary]

    :param start_of_range: The start date.
    :param end_of_range: The end date
    :return: The list of dates inclusive.
    """

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


def beginning_of_week(date_: date, week_starts_on: int = 7, iso: bool = True) -> date:
    """
    Find the first day of the week which contains date_.

    Python standard days of the week have a range of 0 - 6, with 0 being Monday.
    Iso standard days of the week have a range of 1 - 7, with 1 being Monday.

    :param date_: Date reference to find the first day of the week.
    :param week_starts_on: Index first day of the week, defaults to 7, Sunday
    :param iso: Use iso week index. Defaults to ``True``.
    :raises ValueError: Invalid `week_starts_on` value.
    :return: The first day of the week that contains `date_`
    """
    logging.debug(
        "beginning_of_week(date_=%s, week_starts_on=%s, iso=%s)",
        date_,
        week_starts_on,
        iso,
    )
    if iso:
        start_index = 1
        end_index = 8
        dow_index = date_.isoweekday() - 1
    else:
        start_index = 0
        end_index = 7
        dow_index = date_.weekday()
    week_index = list(range(start_index, end_index, 1))
    if week_starts_on not in week_index:
        raise ValueError(f"week_starts_on of {week_starts_on} is not valid. iso={iso}")
    distance, _ = distance_in_list(
        week_index, dow_index, -1, simple_filter(week_starts_on)
    )
    if distance is not None:
        new_date = date_ - timedelta(hours=24 * distance)
        return new_date
    raise ValueError("could not find date.")


def end_of_week(date_: date, week_starts_on: int = 7, iso: bool = True) -> date:
    """
    Find the last day of the week which contains date_.

    Python standard days of the week have a range of 0 - 6, with 0 being Monday.
    Iso standard days of the week have a range of 1 - 7, with 1 being Monday.

    :param date_: Date reference to find the last day of the week.
    :param week_starts_on: Index first day of the week, defaults to 7, Sunday
    :param iso: Use iso week index. Defaults to ``True``.
    :raises ValueError: Invalid `week_starts_on` value.
    :return: The last day of the week that contains `date_`
    """
    logging.debug(
        "end_of_week(date_=%s, week_starts_on=%s, iso=%s)",
        date_,
        week_starts_on,
        iso,
    )
    s_o_w = beginning_of_week(date_=date_, week_starts_on=week_starts_on, iso=iso)
    e_o_w = s_o_w + timedelta(hours=24 * 6)
    return e_o_w


# def pad_to_end_of_week(date_: date) -> date:
#     dow_index = 6 - date_.weekday()
#     new_date = date_ + timedelta(hours=24 * dow_index)
#     return new_date


# def iso_date_now(tz=dateutil.tz.UTC):
#     return datetime.now(tz).date().isoformat()


def tz_aware_utcnow() -> datetime:
    """
    Enforce adding timezone to utcnow. Use this over utcnow.

    https://docs.python.org/3/library/datetime.html#datetime.datetime.now

    :return: A datetime representing a timezone aware :func:`datetime.utcnow`
    """
    return datetime.now(tz.UTC)  # type: ignore
