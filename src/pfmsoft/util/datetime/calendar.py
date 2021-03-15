# TODO change chunk use to more-itertools
from datetime import date
from typing import List, Sequence, Tuple

from more_itertools import chunked

# from pfm_util.collection.misc import chunk
from pfmsoft.util.datetime.datetime import (
    beginning_of_week,
    end_of_week,
    range_of_dates,
)


class CalendarMaker:
    """"""

    # TODO handle differrent starting dow. currently only does mondays
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.padded_range = get_padded_dates_in_range(start_date, end_date)

    def generate_calendar_tokens(self, marked_days: List[date]) -> List[List[str]]:
        date_list = blank_unmarked_dates(self.padded_range, marked_days)
        week_headers = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        split_dates = split_dates_to_weeks(date_list)
        split_dates.insert(0, week_headers)
        return split_dates


# def pad_to_beginning_of_week(date_: date) -> date:
#     dow_index = date_.weekday()
#     new_date = date_ - timedelta(hours=24 * dow_index)
#     return new_date


# def pad_to_end_of_week(date_: date) -> date:
#     dow_index = 6 - date_.weekday()
#     new_date = date_ + timedelta(hours=24 * dow_index)
#     return new_date


def get_padded_dates_in_range(start_date: date, end_date: date) -> Sequence[date]:
    # TODO change to get_full_weeks_in_range(start,end,bow,iso)
    padded_start = beginning_of_week(start_date, 0, False)
    padded_end = end_of_week(end_date, 0, False)
    date_range = range_of_dates(padded_start, padded_end)
    return date_range


def blank_unmarked_dates(
    date_list: List[date],
    marked_dates: List[date],
    blank_placeholder: str = "--",
    marked_date_fmt: str = "%d",
) -> List[str]:
    new_date_list = []
    for date_ in date_list:
        if date_ in marked_dates:
            new_date_list.append(date_.strftime(marked_date_fmt))
        else:
            new_date_list.append(blank_placeholder)
    return new_date_list


def split_dates_to_weeks(date_list: Sequence[str]) -> List[List[str]]:
    new_list = list(chunked(date_list, 7))
    return new_list


def reorder_dow_list(dow_start: str):
    base_list: Tuple[str, str, str, str, str, str, str] = (
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    )
    new_start_index = base_list.index(dow_start)
    split_beginning = base_list[:new_start_index]
    split_end = base_list[new_start_index:]
    new_dow_list = split_end + split_beginning
    return new_dow_list
