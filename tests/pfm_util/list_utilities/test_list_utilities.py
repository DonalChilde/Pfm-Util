from dataclasses import dataclass

import pytest

from pfm_util.list_utilities.list_utilities import (
    distance_in_list,
    simple_filter,
    wrap_range,
)


def test_wrap_range():
    range_gen = wrap_range(0, 10, 6, 1)
    as_list = list(range_gen)
    expected = [6, 7, 8, 9, 0, 1, 2, 3, 4, 5]
    assert as_list == expected

    range_gen = wrap_range(0, 10, 6, -1)
    as_list = list(range_gen)
    expected = [6, 5, 4, 3, 2, 1, 0, 9, 8, 7]
    assert as_list == expected

    range_gen = wrap_range(-2, 10, 6, -1)
    as_list = list(range_gen)
    print(as_list)
    expected = [6, 5, 4, 3, 2, 1, 0, -1, -2, 9, 8, 7]
    assert as_list == expected


def test_distance_in_list():
    list_data = list(range(10))

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
    print(list_data)
    for input_data in input_list:

        distance, index = distance_in_list(
            list_data,
            input_data.start_index,
            input_data.step,
            simple_filter(input_data.desired_value),
        )
        assert distance == input_data.expected_distance
        print(
            f"{input_data.desired_value} (at index {index}) is {distance} away from start_index {input_data.start_index} with step {input_data.step}"
        )
