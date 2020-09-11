from operator import attrgetter, itemgetter
from typing import (
    Sequence,
    Any,
    Tuple,
    Union,
    List,
    Iterable,
    Dict,
    Callable,
    NamedTuple,
)


SortSpec = NamedTuple("SortSpec", [("sort_key", Union[str, int]), ("reversed", bool)])


def optional_collection(argument, collection_factory):
    if argument is None:
        return collection_factory()
    return argument


def sort_in_place(
    xs: List[Union[Sequence, Any]], specs: Sequence[SortSpec], use_get_item: bool,
):
    if not hasattr(xs, "sort"):
        raise AttributeError(
            "Sortable must be a mutable type with a sort function, e.g. List"
        )
    if use_get_item:
        for key, reverse in reversed(specs):
            xs.sort(key=itemgetter(key), reverse=reverse)
        return xs
    for key, reverse in reversed(specs):
        xs.sort(key=attrgetter(key), reverse=reverse)  # type: ignore
    return xs


def sort_to_new_list(
    xs: Iterable[Union[Sequence, Any]],
    specs: Sequence[Tuple[Union[str, int], bool]],
    use_get_item: bool,
):
    if use_get_item:
        sorted_list = []
        for index, spec in enumerate(reversed(specs)):
            key, reverse = spec
            if index == 0:
                sorted_list = sorted(xs, key=itemgetter(key), reverse=reverse)
            sorted_list = sorted(sorted_list, key=itemgetter(key), reverse=reverse)
        return sorted_list
    sorted_list = []
    for index, spec in enumerate(reversed(specs)):
        key, reverse = spec
        if index == 0:
            sorted_list = sorted(xs, key=itemgetter(key), reverse=reverse)
        sorted_list = sorted(sorted_list, key=attrgetter(key), reverse=reverse)  # type: ignore
    return sorted_list


def index_list_of_dicts(
    data: Sequence[Dict[str, Any]], key_field: str
) -> Dict[str, Dict[str, Any]]:
    # TODO save to utilities
    result = {}
    for item in data:
        key_field_value = item[key_field]  # will error if field not found
        result[str(key_field_value)] = item
    return result


def index_list_of_objects(
    data: Iterable[Union[Sequence, Any]],
    key_field,
    use_get_item: bool,
    cast_index: Callable = None,
):
    """
    Will index a list of objects based on key_field.

    Returns a dict with key based on key_field of object
    
    Parameters
    ----------
    data : Iterable[Union[Sequence, Any]]
        [description]
    key : [type]
        [description]
    use_get_item : bool
        [description]
    cast_index : Callable, optional
        [description], by default None
    
    Returns
    -------
    [type]
        [description]
    """
    if use_get_item:
        indexer = itemgetter(key_field)
    else:
        indexer = attrgetter(key_field)
    result = {}
    for item in data:
        key_field_value = indexer(item)
        if cast_index is not None:
            key_field_value = cast_index(key_field_value)
        result[key_field_value] = item
    return result


def index_list_of_objects_multiple(
    data: Iterable[Union[Sequence, Any]],
    key_field,
    use_get_item: bool,
    cast_index: Callable = None,
) -> Dict[Any, List[Any]]:
    if use_get_item:
        indexer = itemgetter(key_field)
    else:
        indexer = attrgetter(key_field)
    result: Dict[Any, List[Any]] = {}
    for item in data:
        key_field_value = indexer(item)
        if cast_index is not None:
            key_field_value = cast_index(key_field_value)
        indexed_field = result.get(key_field_value, [])
        indexed_field.append(item)
        result[key_field_value] = indexed_field
    return result
