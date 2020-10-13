import logging

import pytest

from pfm_util.collection.sort import (
    SortInstruction,
    index_objects,
    sort_in_place,
    sort_to_new_list,
)

from .misc_test import SomeData

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def test_sort_in_place(caplog):
    caplog.set_level(logging.DEBUG)
    list_1 = ["d", "e", "f"]
    list_2 = ["a", "b", "c"]
    list_3 = ["g", "h", "i"]
    data_lists = [list_1, list_2, list_3]
    primary_sort = SortInstruction(sort_key=1)
    instructions = [primary_sort]
    sort_in_place(data_lists, instructions)
    logging.debug("Sorted Lists: %s", data_lists)
    assert data_lists[0] == list_2

    # secondary sorts
    list_2_a = ["a", "b", "a"]
    list_2_b = ["a", "b", "b"]
    data_lists = [list_1, list_2, list_2_a, list_2_b, list_3]
    primary_sort = SortInstruction(sort_key=1)
    secondary_sort = SortInstruction(sort_key=2)
    instructions = [primary_sort, secondary_sort]
    sort_in_place(data_lists, instructions)
    logging.debug("Sorted Lists: %s", data_lists)
    assert data_lists[0] == list_2_a
    assert data_lists[1] == list_2_b
    assert data_lists[2] == list_2

    # itemgetter with dict, descending
    dict_1 = {"pri": "a", "sec": "b", "ter": "c"}
    dict_2 = {"pri": "d", "sec": "e", "ter": "f"}
    dict_3 = {"pri": "g", "sec": "h", "ter": "i"}
    dict_4 = {"pri": "j", "sec": "k", "ter": "l"}
    dict_5 = {"pri": "m", "sec": "n", "ter": "o"}
    data_lists = [dict_1, dict_2, dict_3, dict_4, dict_5]
    primary_sort = SortInstruction(sort_key="sec", descending=True)
    instructions = [primary_sort]
    sort_in_place(data_lists, instructions)
    logging.debug("Sorted Lists: %s", data_lists)
    assert data_lists[0] == dict_5

    # attrgetter
    data_1 = SomeData(1, "a")
    data_2 = SomeData(2, "b")
    data_3 = SomeData(3, "c")
    data_lists = [data_1, data_2, data_3]
    primary_sort = SortInstruction(sort_key="data_2", descending=True)
    instructions = [primary_sort]
    sort_in_place(data_lists, instructions, use_itemgetter=False)
    logging.debug("Sorted Lists: %s", data_lists)
    assert data_lists[0] == data_3

    # No sort method
    with pytest.raises(AttributeError):
        no_sort = int
        primary_sort = SortInstruction(sort_key="data_2", descending=True)
        sort_in_place(no_sort, [primary_sort], use_itemgetter=True)


def test_sort_to_new_list(caplog):
    caplog.set_level(logging.DEBUG)

    list_1 = ["d", "e", "f"]
    list_2 = ["a", "b", "c"]
    list_3 = ["g", "h", "i"]
    data_lists = [list_1, list_2, list_3]
    primary_sort = SortInstruction(sort_key=1)
    instructions = [primary_sort]
    new_list = sort_to_new_list(data_lists, instructions)
    logging.debug("Sorted Lists: %s", new_list)
    assert new_list[0] == list_2

    # secondary sorts
    list_2_a = ["a", "b", "a"]
    list_2_b = ["a", "b", "b"]
    data_lists = [list_1, list_2, list_2_a, list_2_b, list_3]
    primary_sort = SortInstruction(sort_key=1)
    secondary_sort = SortInstruction(sort_key=2)
    instructions = [primary_sort, secondary_sort]
    new_list = sort_to_new_list(data_lists, instructions)
    logging.debug("Sorted Lists: %s", new_list)
    assert new_list[0] == list_2_a
    assert new_list[1] == list_2_b
    assert new_list[2] == list_2

    # itemgetter with dict, descending
    dict_1 = {"pri": "a", "sec": "b", "ter": "c"}
    dict_2 = {"pri": "d", "sec": "e", "ter": "f"}
    dict_3 = {"pri": "g", "sec": "h", "ter": "i"}
    dict_4 = {"pri": "j", "sec": "k", "ter": "l"}
    dict_5 = {"pri": "m", "sec": "n", "ter": "o"}
    data_lists = [dict_1, dict_2, dict_3, dict_4, dict_5]
    primary_sort = SortInstruction(sort_key="sec", descending=True)
    instructions = [primary_sort]
    new_list = sort_to_new_list(data_lists, instructions)
    logging.debug("Sorted Lists: %s", new_list)
    assert new_list[0] == dict_5

    # attrgetter
    data_1 = SomeData(1, "a")
    data_2 = SomeData(2, "b")
    data_3 = SomeData(3, "c")
    data_lists = [data_1, data_2, data_3]
    primary_sort = SortInstruction(sort_key="data_2", descending=True)
    instructions = [primary_sort]
    new_list = sort_to_new_list(data_lists, instructions, use_itemgetter=False)
    logging.debug("Sorted Lists: %s", new_list)
    assert new_list[0] == data_3


def test_index_objects(caplog):
    caplog.set_level(logging.DEBUG)
    data_1 = [[1, 2, 3], ["a", "b", "c"], [4, 5, 6]]
    data_2 = [
        {"arg1": 1, "arg2": 2, "arg3": 3},
        {"arg1": "a", "arg2": "b", "arg3": "c"},
        {"arg1": 4, "arg2": 5, "arg3": 6},
    ]
    obj_1 = SomeData(1, "a")
    obj_2 = SomeData(2, "b")
    obj_3 = SomeData(3, "c")
    obj_4 = SomeData(4, "b")
    data_3 = [obj_1, obj_2, obj_3, obj_4]

    result_1 = index_objects(data_1, 2)
    assert result_1["c"] == ["a", "b", "c"]
    assert result_1["3"] == [1, 2, 3]

    result_2 = index_objects(data_2, "arg2")
    assert result_2["2"] == {"arg1": 1, "arg2": 2, "arg3": 3}

    result_3 = index_objects(data_3, "data_2", use_itemgetter=False)
    assert result_3["a"] == SomeData(1, "a")
    assert len(result_3) == 3

    result_4 = index_objects(
        data_3, "data_2", use_itemgetter=False, preserve_multiple=True
    )
    logging.debug("result_4: %s", result_4)
    assert result_4["a"] == [SomeData(1, "a")]
    assert result_4["b"] == [SomeData(2, "b"), SomeData(4, "b")]
    assert len(result_4) == 3

    result_5 = index_objects(data_1, 2, cast_index=None)
    assert result_5[3] == [1, 2, 3]
    assert result_5["c"] == ["a", "b", "c"]
