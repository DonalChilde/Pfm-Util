import contextlib
from collections import OrderedDict
from functools import wraps
from string import Template
from time import perf_counter_ns
from typing import List, Optional, Sequence


class Timer1:
    """[summary]

    (time_stamp_ns,elapsed)
    """

    def __init__(self, timer_name: str = ""):
        self.timer_name = timer_name
        self.event_record: OrderedDict = OrderedDict()

    def start_timer(self):
        self.event_record = OrderedDict()
        self.start_event("_total_time")

    def end_timer(self):
        total = self.event_record.get("_total_time", None)
        if total is None:
            raise ValueError("Timer has not been started yet.")
        self.event_record["_total_time"]["finish"] = perf_counter_ns()

    def start_event(self, label):
        self.event_record[label] = {"start": perf_counter_ns(), "finish": 0}

    def finish_event(self, label: str):
        if label in self.event_record:
            self.event_record[label]["finish"] = perf_counter_ns()
        else:
            raise ValueError(f"{label} not a valid label.")

    def get_event_time(self, label):
        if label in self.event_record:
            lap = self.event_record[label]["finish"] - self.event_record[label]["start"]
            return lap
        else:
            raise ValueError(f"{label} not a valid label.")

    def format_ns(self, ns, timespec="seconds"):
        if timespec == "seconds":
            return f"{ns/1000000000:9f} seconds."

    def simple_event_message(self, label, timespec="seconds"):
        formatted_nano = self.format_ns(self.get_event_time(label), timespec)
        print(f"{label} took {formatted_nano}")

    def simple_timer_message(self, timespec="seconds"):
        total = self.event_record.get("_total_time", None)
        if total is None:
            raise ValueError("Timer has not been started yet.")
        if total["finish"] == 0:
            raise ValueError("Timer has not been ended yet.")
        formatted_nano = self.format_ns(self.get_event_time("_total_time"))
        print(f"{self.timer_name} took {formatted_nano}")


@contextlib.contextmanager
def context_timer(label, time_spec="seconds"):
    start = perf_counter_ns()
    yield
    if time_spec == "nanoseconds":
        print(f"{label} took {perf_counter_ns()-start} nano seconds.")
    else:
        print(f"{label} took {(perf_counter_ns()-start)/1000000000:9f} seconds.")


def timeit(method, logger=None):
    # https://rednafi.github.io/digressions/python/2020/04/21/python-concurrent-futures.html
    @wraps(method)
    def wrapper(*args, **kwargs):
        start = perf_counter_ns()
        result = method(*args, **kwargs)
        if logger is None:
            print(
                f"{method.__name__} => {(perf_counter_ns()-start)/1000000000:9f} seconds."
            )
        else:
            dur = f"{(perf_counter_ns()-start)/1000000000:9f}"
            logger.info("%s => %s seconds.", method.__name__, dur)

        return result

    return wrapper


class Interval:
    def __init__(self, name, start=0, end=0, time_unit: str = "ns"):
        self.name: str = name
        self.start: int = start
        self.end: int = end
        self.time_unit = time_unit

    def duration(self) -> int:
        if self.end == 0 or self.start == 0:
            raise ValueError(f"Start or End not set.{self!r}")
        return self.end - self.start

    def duration_string(
        self, time_spec: Optional[str] = "seconds", with_units: bool = True
    ) -> str:
        """
        [summary]

        [extended_summary]

        :param time_spec: Units used to format the duration, defaults to "seconds"
        :param with_units: Include duration units in the msg, defaults to True
        :return: The string representing a duration.
        """

        if self.time_unit == "ns":
            formatted = self.format_ns(self.duration, time_spec)
            if with_units:
                return f"{formatted} {time_spec}"
            return f"{formatted}"
        return str(self.duration)

    @staticmethod
    def format_ns(ns, time_spec="seconds") -> str:
        if time_spec == "seconds":
            return f"{ns/1000000000:9f}"
        return str(ns)

    @staticmethod
    def simple_template_string():
        # predefined template string
        return "${name} took ${duration_string}"

    @staticmethod
    def interval_message(
        interval,
        template_string: Optional[str] = None,
        time_spec: Optional[str] = "seconds",
        with_units=True,
    ) -> str:
        """
        Makes a string message for the last interval.

        Template string offers `name` and `duration_string` fields.

        :param interval: [description]
        :param template_string: The `string.Template` string used to format the message, by default uses
            template str supplied by `Timer.simple_template_string()`.
        :param time_spec: Units used to format the duration, defaults to "seconds"
        :param with_units: Include duration units in the msg, defaults to True
        :return: A string describing the last interval.
        """

        if template_string is None:
            template_string = Interval.simple_template_string()
        template = Template(template_string)
        return template.safe_substitute(
            name=interval.name,
            duration_string=interval.duration_string(time_spec, with_units),
        )


class Timer:
    def __init__(self, name):
        self._name = name
        self._intervals: List[Interval] = []
        self._start_timestamp = None
        self._end_timestamp = None

    def start(self):
        # make new interval named _start, set start, set as self._intervals[0]
        # start as perf_counter_ns() on main timer
        # set start_timestamp as now() on main timer

        pass

    def stop(self):
        # make new interval named _end, via self.new_interval

        pass

    def new_interval(self, name: Optional[str] = None):
        # if self._intervals[-1].name == "_end" raise valueerror
        # makes a new Interval, sets start to end of previous interval, or start of parent Timer if first interval.
        # sets end to perf_counter_ns()
        pass

    def elapsed(self) -> Interval:
        # check to see if timer has ended, or if just getting elapsed time.
        elapsed_interval = Interval(
            "elapsed", self._intervals[0].start, perf_counter_ns()
        )
        return elapsed_interval

    def print_total(self, template_string: str, time_spec: str = "seconds"):
        # print the template string with available keywords:
        # name, duration_string
        pass

    def interval_messages(
        self,
        template_string: str,
        time_spec: str = "seconds",
        include_no_name: bool = False,
    ) -> Sequence[str]:
        # print the template string with available keywords:
        # name, duration_string
        # option to exclude intervals that had no name given.
        # if printed, intervals with no name use list index as name.
        template = Template(template_string)
        raise NotImplementedError
