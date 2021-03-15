from datetime import date, datetime, timedelta

from pfmsoft.util.datetime.calendar import (
    CalendarMaker,
    blank_unmarked_dates,
    get_padded_dates_in_range,
    range_of_dates,
    reorder_dow_list,
    split_dates_to_weeks,
)

# def test_dow_list():
#     maker = CalendarMaker("foo", "bar", "Tuesday")
#     new_dow = "Tuesday"
#     new_dow_list = maker.dow_list(new_dow)
#     print(new_dow_list)
#     assert (
#         str(new_dow_list)
#         == "('Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday')"
#     )
#     new_dow = "Sunday"
#     new_dow_list = maker.dow_list(new_dow)
#     print(new_dow_list)
#     assert (
#         str(new_dow_list)
#         == "('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')"
#     )


# def test_range_of_dates():
#     start_date = date(2019, 1, 1)
#     end_date = date(2019, 1, 5)
#     date_range = range_of_dates(start_date, end_date)
#     print(date_range)
#     start_date = date(2019, 1, 5)
#     end_date = date(2019, 1, 1)
#     date_range = range_of_dates(start_date, end_date)
#     print(date_range)
#     start_date = date(2019, 1, 1)
#     end_date = date(2019, 1, 1)
#     date_range = range_of_dates(start_date, end_date)
#     print(date_range)
#     start_date = datetime.today().date()
#     end_date = date(2019, 12, 25)
#     date_range = range_of_dates(start_date, end_date)
#     print(date_range)
#     start_of_range = datetime.today().date()
#     end_of_range = start_of_range + timedelta(days=3)
#     date_range = range_of_dates(start_of_range, end_of_range)
#     print(date_range)
#     start_of_range = datetime.today().date()
#     end_of_range = start_of_range - timedelta(days=3)
#     date_range = range_of_dates(start_of_range, end_of_range)
#     print(date_range)
#     # assert False


def test_get_padded_dates_in_range():

    start_date = date(2019, 3, 1)
    end_date = date(2019, 4, 1)
    date_range = get_padded_dates_in_range(start_date, end_date)
    print(
        f"start_date {start_date}({start_date.weekday()}) end_date {end_date}({end_date.weekday()})"
    )
    print(
        f"date range start {date_range[0]}({date_range[0].weekday()}) date range end {date_range[-1]}({date_range[-1].weekday()})"
    )
    print(date_range)
    # converted_range = [x.date() for x in date_range]
    assert date_range == [
        date(2019, 2, 25),
        date(2019, 2, 26),
        date(2019, 2, 27),
        date(2019, 2, 28),
        date(2019, 3, 1),
        date(2019, 3, 2),
        date(2019, 3, 3),
        date(2019, 3, 4),
        date(2019, 3, 5),
        date(2019, 3, 6),
        date(2019, 3, 7),
        date(2019, 3, 8),
        date(2019, 3, 9),
        date(2019, 3, 10),
        date(2019, 3, 11),
        date(2019, 3, 12),
        date(2019, 3, 13),
        date(2019, 3, 14),
        date(2019, 3, 15),
        date(2019, 3, 16),
        date(2019, 3, 17),
        date(2019, 3, 18),
        date(2019, 3, 19),
        date(2019, 3, 20),
        date(2019, 3, 21),
        date(2019, 3, 22),
        date(2019, 3, 23),
        date(2019, 3, 24),
        date(2019, 3, 25),
        date(2019, 3, 26),
        date(2019, 3, 27),
        date(2019, 3, 28),
        date(2019, 3, 29),
        date(2019, 3, 30),
        date(2019, 3, 31),
        date(2019, 4, 1),
        date(2019, 4, 2),
        date(2019, 4, 3),
        date(2019, 4, 4),
        date(2019, 4, 5),
        date(2019, 4, 6),
        date(2019, 4, 7),
    ]


def test_blank_unmarked_dates():
    start_date = date(2019, 3, 1)
    end_date = date(2019, 4, 1)
    date_range = get_padded_dates_in_range(start_date, end_date)
    marked_dates = [date(2019, 3, 5), date(2019, 4, 1)]
    blanked_list = blank_unmarked_dates(date_range, marked_dates)
    # print(blanked_list)
    assert blanked_list == [
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "05",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
        "01",
        "--",
        "--",
        "--",
        "--",
        "--",
        "--",
    ]


def test_split_dates_to_weeks():
    start_date = date(2019, 3, 1)
    end_date = date(2019, 4, 1)
    date_range = get_padded_dates_in_range(start_date, end_date)
    marked_dates = [date(2019, 3, 5), date(2019, 4, 1)]
    blanked_list = blank_unmarked_dates(date_range, marked_dates)
    split_list = split_dates_to_weeks(blanked_list)
    assert split_list == [
        ["--", "--", "--", "--", "--", "--", "--"],
        ["--", "05", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--"],
        ["01", "--", "--", "--", "--", "--", "--"],
    ]
    # print(split_dates_to_weeks(blanked_list))


def test_CalendarMaker():
    start_date = date(2019, 3, 1)
    end_date = date(2019, 4, 1)
    maker = CalendarMaker(start_date, end_date)
    marked_dates = []
    short_calendar = maker.generate_calendar_tokens(marked_dates)
    assert short_calendar == [
        ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
        ["--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--"],
    ]
    start_date = date(2019, 3, 1)
    end_date = date(2019, 4, 1)
    maker = CalendarMaker(start_date, end_date)
    marked_dates = [
        date(2019, 3, 1),
        date(2019, 3, 5),
        date(2019, 4, 1),
        date(2019, 3, 31),
    ]
    short_calendar = maker.generate_calendar_tokens(marked_dates)
    # print(short_calendar)
    assert short_calendar == [
        ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
        ["--", "--", "--", "--", "01", "--", "--"],
        ["--", "05", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "31"],
        ["01", "--", "--", "--", "--", "--", "--"],
    ]


def test_reorder_dow_list():
    new_order = reorder_dow_list("Tuesday")
    print(new_order)
