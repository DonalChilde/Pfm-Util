import logging
from dataclasses import dataclass
from operator import attrgetter, itemgetter
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

T = TypeVar("T")

SortSpec = NamedTuple("SortSpec", [("sort_key", Union[str, int]), ("reversed", bool)])


@dataclass
class SortInstruction:
    sort_key: Union[str, int]
    descending: bool = False


def optional_object(
    argument: Union[None, T], object_factory: Callable[..., T], *args, **kwargs
) -> T:
    """
    A convenience method for initializing optional arguments.

    Meant to be used when solving the problem of passing an object, e.g. a List
    when the object is expected to be a passed in list or a default empty list.
    So make the default value None, and call this function to initialize the object.

    :example:
    @dataclass
    class SomeData:
        data_1: int
        data_2: str

    class MyClass:
        def __init__(
            self,
            arg1: int,
            arg2: Optional[List[str]] = None,
            arg3: Optional[Dict[str, int]] = None,
            arg4: Optional[SomeData] = None,
        ):
            default_somedata = {"data_1": 1, "data_2": "two"}
            self.arg1 = arg1
            self.arg2: List[str] = collection_utilities.optional_object(
                arg2, list, ["a", "b", "c"]
            )
            self.arg3: Dict[str, int] = collection_utilities.optional_object(arg3, dict)
            self.arg4: SomeData = collection_utilities.optional_object(
                arg4, SomeData, **default_somedata
            )

    :param argument: An argument that is an object that may be None.
    :param object_factory: Factory function used to create the object.
    :param `*args`: Optional arguments passed to factory function.
    :param `**kwargs`: Optional keyword arguments passed to factory function.
    :return: The initialized object.
    """

    if argument is None:
        return object_factory(*args, **kwargs)
    return argument


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


def search_list_of_dicts(
    data: List[Dict[Any, Any]],
    search_key,
    search_value,
    target_key,
    target_default_value,
):
    # returns target default value if unable to match search_key and or value_key
    # TODO convert to itemgetter etc.
    for item in data:
        if search_key in item:
            if item[search_key] == search_value:
                return item.get(target_key, target_default_value)
    return target_default_value
