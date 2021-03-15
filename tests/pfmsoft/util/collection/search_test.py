import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from pfmsoft.util.collection.search import distance_in_list
from pfmsoft.util.filter.filter import simple_filter

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def test_distance_in_list(caplog):
    caplog.set_level(logging.DEBUG)
    list_data = list(range(10))
    # List_data: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    @dataclass
    class InputData:
        desired_value: int
        start_index: int
        step: int
        expected_distance: int

    input_list = [
        InputData(desired_value=5, start_index=4, step=1, expected_distance=1),
        InputData(desired_value=5, start_index=5, step=1, expected_distance=0),
        InputData(desired_value=5, start_index=6, step=1, expected_distance=9),
        InputData(desired_value=5, start_index=7, step=1, expected_distance=8),
        InputData(desired_value=5, start_index=8, step=1, expected_distance=7),
        InputData(desired_value=5, start_index=9, step=1, expected_distance=6),
        InputData(desired_value=5, start_index=0, step=1, expected_distance=5),
        InputData(desired_value=5, start_index=1, step=1, expected_distance=4),
        InputData(desired_value=5, start_index=2, step=1, expected_distance=3),
        InputData(desired_value=5, start_index=3, step=1, expected_distance=2),
        InputData(desired_value=5, start_index=4, step=-1, expected_distance=9),
        InputData(desired_value=5, start_index=5, step=-1, expected_distance=0),
        InputData(desired_value=5, start_index=6, step=-1, expected_distance=1),
        InputData(desired_value=5, start_index=7, step=-1, expected_distance=2),
        InputData(desired_value=5, start_index=8, step=-1, expected_distance=3),
        InputData(desired_value=5, start_index=9, step=-1, expected_distance=4),
        InputData(desired_value=5, start_index=0, step=-1, expected_distance=5),
        InputData(desired_value=5, start_index=1, step=-1, expected_distance=6),
        InputData(desired_value=5, start_index=2, step=-1, expected_distance=7),
        InputData(desired_value=5, start_index=3, step=-1, expected_distance=8),
    ]
    logger.debug("List_data: %s", list_data)
    for input_data in input_list:

        distance, index = distance_in_list(
            list_data,
            input_data.start_index,
            input_data.step,
            simple_filter(input_data.desired_value),
        )

        logger.debug(
            "%s (at index %s) is %s away from start_index %s with step %s",
            input_data.desired_value,
            index,
            distance,
            input_data.start_index,
            input_data.step,
        )
        assert distance == input_data.expected_distance
    list_data_str = [
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
    ]
    input_list_str = [
        InputData(desired_value="five", start_index=4, step=1, expected_distance=0),
        InputData(desired_value="five", start_index=5, step=1, expected_distance=9),
        InputData(desired_value="five", start_index=6, step=1, expected_distance=8),
        InputData(desired_value="five", start_index=7, step=1, expected_distance=7),
        InputData(desired_value="five", start_index=8, step=1, expected_distance=6),
        InputData(desired_value="five", start_index=9, step=1, expected_distance=5),
        InputData(desired_value="five", start_index=0, step=1, expected_distance=4),
        InputData(desired_value="five", start_index=1, step=1, expected_distance=3),
        InputData(desired_value="five", start_index=2, step=1, expected_distance=2),
        InputData(desired_value="five", start_index=3, step=1, expected_distance=1),
        InputData(desired_value="five", start_index=4, step=-1, expected_distance=0),
        InputData(desired_value="five", start_index=5, step=-1, expected_distance=1),
        InputData(desired_value="five", start_index=6, step=-1, expected_distance=2),
        InputData(desired_value="five", start_index=7, step=-1, expected_distance=3),
        InputData(desired_value="five", start_index=8, step=-1, expected_distance=4),
        InputData(desired_value="five", start_index=9, step=-1, expected_distance=5),
        InputData(desired_value="five", start_index=0, step=-1, expected_distance=6),
        InputData(desired_value="five", start_index=1, step=-1, expected_distance=7),
        InputData(desired_value="five", start_index=2, step=-1, expected_distance=8),
        InputData(desired_value="five", start_index=3, step=-1, expected_distance=9),
    ]
    logger.debug("List_data_str: %s", list_data_str)
    for input_data in input_list_str:

        distance, index = distance_in_list(
            list_data_str,
            input_data.start_index,
            input_data.step,
            simple_filter(input_data.desired_value),
        )

        logger.debug(
            "%s (at index %s) is %s away from start_index %s with step %s",
            input_data.desired_value,
            index,
            distance,
            input_data.start_index,
            input_data.step,
        )
        assert distance == input_data.expected_distance

    distance, index = distance_in_list(list_data_str, 4, 1, simple_filter("Not Here"))
    assert distance is None
    assert index is None
