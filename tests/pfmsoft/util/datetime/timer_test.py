import uuid
from collections import OrderedDict, namedtuple
from dataclasses import dataclass

# from utility_lib.datetime_utilities.timer import Timer, simple_timer
from pfmsoft.util.datetime.timer import Timer, context_timer

NTTEST = namedtuple("NTTEST", ["val1", "val2", "val3"])


@dataclass
class DCTest:
    val1: uuid.UUID
    val2: uuid.UUID
    val3: uuid.UUID


def test_simple_timer():
    print("-----testing simple_timer-----")
    test_range = 1000
    data_gen = uuid.uuid4
    with context_timer("tuple"):
        for x in range(test_range):
            foo = (data_gen(), data_gen(), data_gen())
    with context_timer("empty tuple"):
        for x in range(test_range):
            foo = (0, 0, 0)
    with context_timer("dict"):
        for x in range(test_range):
            foo = {"val1": data_gen(), "val2": data_gen(), "val3": data_gen()}
    with context_timer("empty dict"):
        for x in range(test_range):
            foo: dict = {"val1": 0, "val2": 0, "val3": 0}
    with context_timer("named tuple"):
        for x in range(test_range):
            foo = NTTEST(data_gen(), data_gen(), data_gen())
    with context_timer("empty named tuple"):
        for x in range(test_range):
            foo = NTTEST(0, 0, 0)

    with context_timer("data class"):
        for x in range(test_range):
            foo = DCTest(data_gen(), data_gen(), data_gen())
    with context_timer("empty data class"):
        for x in range(test_range):
            foo = DCTest(0, 0, 0)
    with context_timer("pass"):
        for x in range(test_range):
            pass


def test_ordered_dict_access_time():
    test_range = 10000
    print(
        f"\n-----testing ordereddict last member access time with {test_range} members-----"
    )
    ordered_dict: OrderedDict = OrderedDict()
    last_sample = uuid.uuid4()
    for x in range(test_range):
        sample = uuid.uuid4()
        ordered_dict[sample] = sample
    ordered_dict[last_sample] = sample

    # Note that this takes longer than direct access, but
    # it does not get longer with larger dict sizes. n(1)
    with context_timer("ordered dict reversed"):
        for x in range(100):
            foo = ordered_dict[next(reversed(ordered_dict))]

    with context_timer("ordered dict direct access"):
        for x in range(100):
            foo = ordered_dict[last_sample]


# TODO Timer class has been renamed Timer1, and deprecated. Need to update new Timer class, and write tests.

# def test_timer_class():
#     test_range = 1000
#     data_gen = uuid.uuid4
#     print("\n-----testing Timer class-----")
#     timer = Timer("Test the Timer class")
#     timer.start_timer()

#     timer.start_event("tuple")
#     for x in range(test_range):
#         foo = (data_gen(), data_gen(), data_gen())
#     timer.finish_event("tuple")
#     timer.simple_event_message("tuple")

#     timer.start_event("empty tuple")
#     for x in range(test_range):
#         foo = (0, 0, 0)
#     timer.finish_event("empty tuple")
#     timer.simple_event_message("empty tuple")
#     # timer.simple_timer_message()
#     timer.end_timer()
#     timer.simple_timer_message()
