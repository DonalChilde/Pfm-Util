import logging
from dataclasses import dataclass
from operator import attrgetter, itemgetter
from typing import Any, Callable, Dict, Iterable, List, Sequence, TypeVar, Union

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

T = TypeVar("T")


@dataclass
class SortInstruction:
    sort_key: Union[str, int]
    descending: bool = False


def sort_in_place(
    data: List[T], instructions: Sequence[SortInstruction], use_itemgetter: bool = True
):
    """
    Sort a list of objects in place, e.g a list of lists.

    reference:
    https://docs.python.org/3/howto/sorting.html#ascending-and-descending

    :param data: A mutable collection with a sort function e.g. List.
    :param instructions: Sort "columns" listed in order.
    :param use_itemgetter: Use itemgetter to retrieve sort value, False uses attrgetter.
        Defaults to True.
    :raises AttributeError: Data must be a mutable type with a sort function, e.g. List

    """
    if not hasattr(data, "sort"):
        raise AttributeError(
            "Data must be a mutable type with a sort function, e.g. List"
        )
    for instruction in reversed(instructions):
        if use_itemgetter:
            indexer = itemgetter(instruction.sort_key)
        else:
            indexer = attrgetter(instruction.sort_key)  # type: ignore
        data.sort(key=indexer, reverse=instruction.descending)


def sort_to_new_list(
    data: Iterable[T],
    instructions: Sequence[SortInstruction],
    use_itemgetter: bool = True,
) -> List[T]:
    """
    Sort an iterable to a new list

    reference:
    https://docs.python.org/3/howto/sorting.html#ascending-and-descending

    :param data: An iterable of objects.
    :param instructions: Sort "columns" listed in order.
    :param use_itemgetter: Use itemgetter to retrieve sort value, False uses attrgetter.
        Defaults to True.
    :return: A list of sorted objects
    """

    sorted_list = []
    for index, instruction in enumerate(reversed(instructions)):
        if use_itemgetter:
            indexer = itemgetter(instruction.sort_key)
        else:
            indexer = attrgetter(instruction.sort_key)  # type: ignore
        # index == 0 to handle iterable case, and first sort for sorted_list variable
        if index == 0:
            sorted_list = sorted(data, key=indexer, reverse=instruction.descending)
            continue
        sorted_list = sorted(sorted_list, key=indexer, reverse=instruction.descending)
    return sorted_list


def cast_str(item: Any) -> str:
    """
    A callable to cast an object to string.

    [extended_summary]

    :param item: Object to cast to string.
    :return: String version of item.
    """
    return str(item)


def index_objects(
    data: Iterable[T],
    key_field: Union[str, int],
    use_itemgetter: bool = True,
    cast_index: Callable = cast_str,
    preserve_multiple: bool = False,
) -> Dict[Any, Union[T, List[T]]]:
    """
    Index an iterable of objects based on key_field.

    [extended_summary]

    :param data: [description]
    :param key_field: [description]
    :param use_itemgetter: [description], defaults to True
    :param cast_index: [description], defaults to cast_str
    :param preserve_multiple: [description], defaults to False
    :return: [description]
    """

    if use_itemgetter:
        indexer = itemgetter(key_field)
    else:
        indexer = attrgetter(key_field)  # type: ignore
    result: Dict[Any, Union[T, List[T]]] = {}
    for item in data:
        key_field_value = indexer(item)
        if cast_index is not None:
            key_field_value = cast_index(key_field_value)
        if preserve_multiple:
            indexed_field = result.get(key_field_value, [])
            indexed_field.append(item)  # type: ignore
            result[key_field_value] = indexed_field
        else:
            result[key_field_value] = item
    return result
