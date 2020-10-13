import re
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, Optional

# HHHMMSS = r"(?P<hours>[0-9]+([,.][0-9]+)?)"


def parse_isoformatDuration(durationString: str) -> timedelta:
    pass


def parse_HHMMSS(
    duration_string: str, hm_separator: str = ":", ms_separator: str = ":"
) -> timedelta:
    """

    r"(?P<hours>[0-9]+([,.][0-9]+)?)(:(?P<minutes>[0-6][0-9])(:(?P<seconds>[0-6][0-9](\.[0-9]+)?))?)?"

    """
    check_is_string(duration_string, "duration_string")
    check_is_string(hm_separator, "hm_separator")
    check_is_string(ms_separator, "ms_separator")
    HHHMMSS = (
        r"^(?P<hours>[0-9]+([,.][0-9]+)?)("
        + hm_separator
        + r"(?P<minutes>[0-5][0-9])("
        + ms_separator
        + r"(?P<seconds>[0-5][0-9](\.[0-9]+)?))?)?$"
    )
    pattern = re.compile(HHHMMSS)
    result = pattern.match(duration_string)
    if not result:
        raise ValueError(
            f"{duration_string} does not match pattern HHHMMSS with hours-minutes separator {hm_separator} and minutes-seconds separator {ms_separator}"
        )
    hours_string = result.group("hours") or "0"
    hours_string = hours_string.replace(",", "")
    hours_string = hours_string.replace(".", "")
    hours = int(hours_string)
    minutes = int(result.group("minutes") or "0")
    seconds_string = result.group("seconds") or "0"
    seconds = float(seconds_string)
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def HHHMMSS_to_seconds_int(
    duration_string: str, hm_separator: str = ":", ms_separator: str = ":"
) -> int:
    """Convenience method to convert a duration string to seconds."""
    parsed_value = parse_HHMMSS(
        duration_string=duration_string,
        hm_separator=hm_separator,
        ms_separator=ms_separator,
    )

    return int(parsed_value.total_seconds())


# FIXME move to arg checking lib?
def check_is_string(value: str, arg_name: Optional[str] = None):
    if not isinstance(value, str):
        raise TypeError(
            f"With arg: {arg_name} expected a string, got {value} with type: {type(value)}"
        )


# def parse_HHdotMM_To_timedelta(durationString: str, separator: str = ".") -> timedelta:
#     """
#     parses a string in the format "34.23", assuming HH.MM
#     """
#     hours, minutes = durationString.split(separator)
#     hours, minutes = map(int, (hours, minutes))  # type: ignore
#     return timedelta(hours=hours, minutes=minutes)  # type: ignore


# def parse_HHscMM_to_timedelta(duration_string: str):
#     result = parse_HHdotMM_To_timedelta(duration_string, ":")
#     return result


@dataclass
class TimeDeltaSplit:
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    microseconds: int = 0

    def to_seconds(self) -> int:
        seconds = duration_to_seconds_int(
            self.days, self.hours, self.minutes, self.seconds
        )
        return seconds

    @classmethod
    def from_timedelta(cls, delta: timedelta) -> "TimeDeltaSplit":
        int_seconds = 0
        if delta.days:
            int_seconds = int_seconds + (abs(delta.days) * 86400)
        if delta.seconds:
            int_seconds = int_seconds + delta.seconds
        minutes, seconds = divmod(int_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        microseconds = delta.microseconds
        return cls(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
        )


def split_timedelta(delta: timedelta) -> Dict[str, int]:
    """
    Split a time delta to a dict of days, hours, minutes,seconds, microseconds.
    https://stackoverflow.com/a/17847006/105844

    [extended_summary]

    :param delta: [description]
    :return: [description]
    """
    abs_delta = abs(delta)
    days, rem = divmod(abs_delta, timedelta(days=1))
    hours, rem = divmod(rem, timedelta(hours=1))
    minutes, rem = divmod(rem, timedelta(minutes=1))
    seconds = rem.seconds
    microseconds = rem.microseconds
    return {
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "microseconds": microseconds,
    }


# def timedelta_split(timeDelta: timedelta) -> TimeDeltaSplit:
#     int_seconds = 0
#     if timeDelta.days:
#         int_seconds = int_seconds + (abs(timeDelta.days) * 86400)
#     if timeDelta.seconds:
#         int_seconds = int_seconds + timeDelta.seconds
#     minutes, seconds = divmod(int_seconds, 60)
#     hours, minutes = divmod(minutes, 60)
#     days, hours = divmod(hours, 24)
#     microseconds = timeDelta.microseconds
#     return TimeDeltaSplit(
#         days=days,
#         hours=hours,
#         minutes=minutes,
#         seconds=seconds,
#         microseconds=microseconds,
#     )


def timeDelta_TO_HHMMSS(
    timeDelta: timedelta,
    hm_separator: str = ":",
    ms_separator: str = ":",
    timespec=None,
):
    timeSplit = TimeDeltaSplit.from_timedelta(timeDelta)
    totalHours = (timeSplit.days * 24) + timeSplit.hours
    if timespec == "M":
        return f"{totalHours}{hm_separator}{timeSplit.minutes:02d}"
    if timeSplit.microseconds:
        decimalSecondsString = f".{timeSplit.microseconds:06d}"
    else:
        decimalSecondsString = ""
    return f"{totalHours}{hm_separator}{timeSplit.minutes:02d}{ms_separator}{timeSplit.seconds}{decimalSecondsString}"


def timedelta_To_isoformat(timeDelta: timedelta, strict=True) -> str:
    """
    if strict then limit output fields to PddDThhHmmMss.sS # Not implemeted
    """
    # int_seconds = 0
    # if timeDelta.days:
    #     int_seconds = int_seconds + (abs(timeDelta.days)*86400)
    # if timeDelta.seconds:
    #     int_seconds = int_seconds + timeDelta.seconds
    # minutes, seconds = divmod(int_seconds, 60)
    # hours, minutes = divmod(minutes, 60)
    # days, hours = divmod(hours, 24)
    # microseconds = timeDelta.microseconds
    timeSplit = TimeDeltaSplit.from_timedelta(timeDelta)
    daystext = hourstext = minutestext = secondstext = microtext = ""
    if timeSplit.days:
        daystext = f"{timeSplit.days}D"
    if timeSplit.hours:
        hourstext = f"{timeSplit.hours}H"
    if timeSplit.minutes:
        minutestext = f"{timeSplit.minutes}M"
    if timeSplit.microseconds:
        if not timeSplit.seconds:
            timeSplit.seconds = 0
        microtext = f".{timeSplit.microseconds:06d}"
    if timeSplit.seconds or timeSplit.microseconds:
        secondstext = f"{timeSplit.seconds}{microtext}S"
    if not (
        timeSplit.hours
        or timeSplit.minutes
        or timeSplit.seconds
        or timeSplit.microseconds
    ):
        secondstext = f"{timeSplit.seconds}S"
    isoString = f"P{daystext}T{hourstext}{minutestext}{secondstext}"
    return isoString


def duration_to_seconds_int(
    days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0
) -> int:
    day_seconds = days * 24 * 60 * 60
    hour_seconds = hours * 60 * 60
    minute_seconds = minutes * 60
    return day_seconds + hour_seconds + minute_seconds + seconds
